"""
A module for mining and downloading raw scripts.
"""
import copy
import os
import json
import time

from datetime import datetime

from github import RateLimitExceededException

from iacminer.entities.content import ContentFile, ContentFileEncoder
from iacminer.entities.commit import Commit
from iacminer.entities.file import File
from iacminer.mygit import Git

class ScriptsMiner():

    def __init__(self, fixing_commit: Commit):
        """
        :fixing_commit: a commit to analyze
        """
        self.__g = Git()
        self.__defective_scripts = set()    # set of ContentFile
        self.__unclassified_scripts = set() # set of ContentFile
        self.__load_defective_scripts()
        self.__load_unclassified_scripts()

        self.fixing_commit = fixing_commit

    @property
    def defective_scripts(self):
        return self.__defective_scripts

    @property
    def unclassified_scripts(self):
        return self.__unclassified_scripts
        
    def __load_defective_scripts(self):
        filepath = os.path.join('data','defective_scripts.json')
        if os.path.isfile(filepath):
            with open(filepath, 'r') as infile:
                json_array = json.load(infile)

                for json_obj in json_array:
                    self.__defective_scripts.add(ContentFile(json_obj))

    def __save_defective_scripts(self):

        json_obj = []

        for content in copy.deepcopy(self.__defective_scripts):
            json_content = json.dumps(content, cls=ContentFileEncoder)
            json_obj.append(json.loads(json_content))

        with open(os.path.join('data', 'defective_scripts.json'), 'w') as outfile:
            json.dump(json_obj, outfile)

    def __load_unclassified_scripts(self):
        filepath = os.path.join('data','unclassified_scripts.json')
        if os.path.isfile(filepath):
            with open(filepath, 'r') as infile:
                json_array = json.load(infile)

                for json_obj in json_array:
                    self.__unclassified_scripts.add(ContentFile(json_obj))

    def __save_unclassified_scripts(self):

        json_obj = []

        for content in copy.deepcopy(self.__unclassified_scripts):
            json_content = json.dumps(content, cls=ContentFileEncoder)
            json_obj.append(json.loads(json_content))

        with open(os.path.join('data', 'unclassified_scripts.json'), 'w') as outfile:
            json.dump(json_obj, outfile)

    def __set_defective_scripts(self):
        
        parent_commit = self.fixing_commit.parents[0]
        repo = self.fixing_commit.repo

        
        for file in self.fixing_commit.files:
            
            filename = file.previous_filename if file.previous_filename else file.filename
            for content in self.__g.get_contents(repo, path=filename, ref=parent_commit):
                try:
                    content_file = ContentFile()
                    content_file.commit_sha = parent_commit
                    content_file.repository = repo
                    content_file.filename = content.path
                    content_file.sha = content.sha
                    content_file.decoded_content = self.__g.get_git_blob(repo, content_file.sha)
                    content_file.release_starts_at = file.release_starts_at
                    content_file.release_ends_at = file.release_ends_at

                    if content_file not in self.__defective_scripts:
                        self.__defective_scripts.add(content_file)
                        self.__save_defective_scripts()
                        yield (content_file, True) # True = defect-prone

                except UnicodeDecodeError:
                    print(f'Error decoding content for {self.fixing_commit.repo}/{filename}/commit/{self.fixing_commit.sha}')
                    pass

    def __set_unclassified_scripts(self):
        
        for content in self.__g.get_contents(self.fixing_commit.repo, path='.', ref=self.fixing_commit.parents[0]):
            try:
                content_file = ContentFile()
                content_file.commit_sha = self.fixing_commit.parents[0]
                content_file.repository = self.fixing_commit.repo
                content_file.filename = content.path
                content_file.sha = content.sha
                
                # filtering out non-Ansible files
                if not content_file.is_ansible:
                    continue

                content_file.decoded_content = self.__g.get_git_blob(self.fixing_commit.repo, content.sha)

                if content_file not in self.__defective_scripts:
                    self.__unclassified_scripts.add(content_file)
                    self.__save_unclassified_scripts()
                    yield (content_file, False) # False = defect-free
                    
            except UnicodeDecodeError:
                print(f'Error decoding content for {self.fixing_commit.repo}/{content.path}/commit/{self.fixing_commit.sha}')
                continue

    def mine(self):
        """ 
        Analyze a commit, and extract defective and unclassifieid files \
        from the repository at that point in time.

        :return: yield tuple (content: ContentFile, defective: bool)
        """
        try:
            for script in self.__set_defective_scripts():
                yield script
            
            for script in self.__set_unclassified_scripts():
                yield script

        except RateLimitExceededException:
            print('Rate limit exceeded when downloading files')

            # Wait self.__g.rate_limiting_resettime()
            t = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds() + 60
            print(f'Execution stopped. Quota will be reset in {round(t/60)} minutes')
            time.sleep(t)
            self.__g = Git()