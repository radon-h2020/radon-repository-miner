"""
A module for mining and downloading raw scripts.
"""
import os
import json
import requests
import time

from datetime import datetime

from github import RateLimitExceededException

from requests.exceptions import HTTPError
from iacminer.entities.content import ContentFile, ContentFileEncoder
from iacminer.entities.commit import Commit
from iacminer.entities.file import File
from iacminer.mygit import Git

class ScriptsMiner():

    def __init__(self):
        self.__g = Git()
        self.__defective_scripts = set()    # set of ContentFile
        self.__unclassified_scripts = set() # set of ContentFile
        self.__load_defective_scripts()
        self.__load_unclassified_scripts()

    @property
    def defective_scripts(self):
        return self.__defective_scripts

    @property
    def unclassified_scripts(self):
        return self.__unclassified_scripts

    def __get_content_from_url(self, url) -> str:
        """
        Download the raw content of a file from Github

        :url: the url to the file content

        :return: str file content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.content.decode("utf-8")
            return content
        except HTTPError as _:
            #print(f'HTTP error occurred: {http_err}')
            return None
        except Exception as _:
            #print(f'Other error occurred: {err}')
            return None

    def __set_defective_scripts(self, file: File, commit_sha: str, commit_parent_sha: str, repo: str) -> str:
        filename = file.previous_filename if file.previous_filename else file.filename
        defective_url = file.raw_url.replace(commit_sha, commit_parent_sha)
        defective_url = defective_url.replace(file.filename, filename)

        content = ContentFile()
        
        content.commit_sha = commit_parent_sha
        content.decoded_content = self.__get_content_from_url(defective_url)
        content.filename = file.filename
        content.repository = repo
        content.sha = file.sha

        if content.decoded_content:
            self.__defective_scripts.add(content)

    def __load_defective_scripts(self):
        filepath = os.path.join('data','defective_scripts.json')
        if os.path.isfile(filepath):
            with open(filepath, 'r') as infile:
                json_array = json.load(infile)

                for json_obj in json_array:
                    self.__defective_scripts.add(ContentFile(json_obj))

    def __save_defective_scripts(self):

        json_obj = []

        for content in self.__defective_scripts:
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

        for content in self.__unclassified_scripts:
            json_content = json.dumps(content, cls=ContentFileEncoder)
            json_obj.append(json.loads(json_content))

        with open(os.path.join('data', 'unclassified_scripts.json'), 'w') as outfile:
            json.dump(json_obj, outfile)


    def mine_scripts(self, fixing_commit: Commit):
        """ 
        Analyze a commit, and extract defective and unclassifieid files \
        from the repository at that point in time.
        
        :commit: a commit to analyze

        :return: two set of defective and unclassified files, respectively.
        """
        
        try:
            for file in fixing_commit.files:

                if file in self.__defective_scripts.union(self.__unclassified_scripts):
                    continue

                self.__set_defective_scripts(file, fixing_commit.sha, fixing_commit.parents[0], fixing_commit.repo)
                
                #for content in self.__g.get_contents(fixing_commit.repo, path='.', ref=fixing_commit.sha):
                for content in self.__g.get_contents(fixing_commit.repo, path='.', ref=fixing_commit.parents[0]):
                    content = ContentFile(content)
                    content.commit_sha = fixing_commit.sha
                    content.repository = fixing_commit.repo

                    # filtering out non-Ansible files
                    if not content.is_ansible:
                        continue

                    #if any(d.get('filename', None) == content.filename for d in self.__defective_scripts):
                    if content not in self.__defective_scripts:
                        self.__unclassified_scripts.add(content)
                    
            if len(self.__defective_scripts):
                self.__save_defective_scripts()

            if len(self.__unclassified_scripts):
                self.__save_unclassified_scripts()
        
        except RateLimitExceededException:
            print('Rate limit exceeded when downloading files')

            if len(self.__defective_scripts):
                self.__save_defective_scripts()

            if len(self.__unclassified_scripts):
                self.__save_unclassified_scripts()

            # Wait self.__g.rate_limiting_resettime()
            t = (datetime.fromtimestamp(self.__g.rate_limiting_resettime) - datetime.now()).total_seconds() + 10
            print(f'Execution stopped. Quota will be reset in {round(t/60)} minutes')
            time.sleep(t)

        return self.__defective_scripts, self.__unclassified_scripts
        