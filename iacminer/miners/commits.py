"""
A module for mining fixing commits.
"""
import copy
import github
import json
import os
import re
import time

from datetime import datetime
from requests.exceptions import ReadTimeout

from pydriller.repository_mining import GitRepository, RepositoryMining
from pydriller.domain.commit import ModificationType

from iacminer import filters
from iacminer.entities.file import DefectiveFile

from iacminer.mygit import Git

class CommitsMiner():

    def __init__(self, git_repo: GitRepository, branch: str='master'):
        """
        :git_repo: a GitRepository object
        """
        self.__commits_closing_issues = set() # Set of commits sha closing issues
        self.__commits = []

        self.branch = branch
        self.repo = git_repo
        owner_repo = str(git_repo.path).split('/')[1:]
        self.repo_name = f'{owner_repo[0]}/{owner_repo[1]}'
        self.repo_path = str(git_repo.path)
        
        self.defect_prone_files = dict()
        self.defect_free_files = dict()
        
        # Get commits for repository        
        for commit in RepositoryMining(self.repo_path).traverse_commits():
            self.__commits.append(commit.hash)

    def __set_commits_closing_issues(self, retry=0):
        """ 
        Analyze a repository, and set the commits that fix some issues \
        by looking at the commit that explicitly closes or fixes those issues.
        """
        try:
            g = Git()
        except Exception:
            if retry == 2:
                return
                    
            self.__set_commits_closing_issues(retry + 1)

        for issue in g.get_issues(self.repo_name):
            if not issue:
                continue
            try:
                issue_events = issue.get_events()

                if issue_events is None or issue_events.totalCount == 0:
                    return None
                
                for e in issue_events: 
                    is_merged = e.event.lower() == 'merged'
                    is_closed = e.event.lower() == 'closed'

                    if (is_merged or is_closed) and e.commit_id:
                        self.__commits_closing_issues.add(e.commit_id)

            except ReadTimeout:
                pass                
   
    def __label_files(self, file: DefectiveFile):
        """
        Traverse the commits from the fixing commit to the beginning of the project,
        and label the files as defect-prone or defect-free.
        """
        filepath = file.filepath
        defect_prone = True

        for commit in RepositoryMining(self.repo_path, from_commit=file.fix_commit, reversed_order=True).traverse_commits():
            
            # Label current filepath
            if filepath and commit.hash != file.fix_commit:
                if defect_prone:
                    self.defect_prone_files.setdefault(commit.hash, set()).add(filepath)
                else:
                    self.defect_free_files.setdefault(commit.hash, set()).add(filepath)

            # Handle file renaming
            for modified_file in commit.modifications:
                
                if not filepath:
                    continue
                
                if filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
        
                filepath = modified_file.old_path
            
            # From here on the file is defect_free
            if commit.hash == file.bic_commit:
                defect_prone = False

    def __save_fixing_commit(self, commit):
        DESTINATION_PATH = os.path.join('data', 'fixing_commits.json')

        obj = []
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                obj = json.load(in_file)
        
        obj.append(
            {
                'repo': self.repo_name,
                'hash': commit.hash,
                'msg': commit.msg
            }
        )

        with open(DESTINATION_PATH, 'w') as out:
            json.dump(obj, out)

    def find_defective_files(self):
       
        renamed_files = {}
        defective_files = []

        for commit in RepositoryMining(self.repo_path, reversed_order=True).traverse_commits():
            
            is_fixing_commit = commit.hash in self.__commits_closing_issues

            modified_ansible_files = []

            # Filter Modified Ansible files
            for modified_file in commit.modifications:
                
                if not filters.is_ansible_file(modified_file.new_path):
                    continue
                
                if modified_file.change_type == ModificationType.ADD:
                    continue

                if modified_file.change_type == ModificationType.DELETE:
                    continue

                if modified_file.change_type == ModificationType.RENAME:
                    if modified_file.old_path in renamed_files:
                        renamed_files[modified_file.old_path] = renamed_files.get(modified_file.new_path, modified_file.new_path)
                    elif is_fixing_commit:
                        renamed_files[modified_file.old_path] = modified_file.new_path
                    
                modified_ansible_files.append(modified_file)

            if not is_fixing_commit or not modified_ansible_files:
                continue
            
            self.__save_fixing_commit(commit)

            for modified_file in modified_ansible_files:
               
                buggy_inducing_commits = self.repo.get_commits_last_modified_lines(commit, modified_file)
                
                if not buggy_inducing_commits:
                    continue
                
                # Get the index of the oldest commit among those that induced the bug
                min_idx = len(self.__commits)-1
                for hash in buggy_inducing_commits[modified_file.new_path]:
                    idx = self.__commits.index(hash)
                    if idx < min_idx:
                        min_idx = idx
                
                # First buggy inducing commit hash
                oldest_bic_hash = self.__commits[min_idx]

                df = DefectiveFile(renamed_files.get(modified_file.new_path, modified_file.new_path),
                                   bic_commit=oldest_bic_hash,
                                   fix_commit=commit.hash)

                try:
                    # Get defective file
                    idx = defective_files.index(df)
                    df = defective_files[idx]

                    # If the oldest buggy inducing commit found in the previous step is 
                    # older than a bic saved previously, then replace it
                    idx = self.__commits.index(df.bic_commit)
                    if min_idx < idx:  
                        df.bic_commit = oldest_bic_hash  

                except ValueError: # defective file not present in list
                    defective_files.append(df)

        return defective_files

    def mine(self):
        """ 
        Analyze a repository, yielding buggy inducing commits.
        """

        self.__set_commits_closing_issues()
        
        if self.__commits_closing_issues:
            for file in self.find_defective_files():
                self.__label_files(file)