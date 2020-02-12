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

    def __init__(self, git_repo: GitRepository):
        """
        :git_repo: a GitRepository object
        """
        self.__commits_closing_issues = set() # Set of commits sha closing issues
        self.__commits = []
        self.__releases = []

        self.repo = git_repo
        owner_repo = str(git_repo.path).split('/')[1:]
        self.repo_name = f'{owner_repo[0]}/{owner_repo[1]}'
        self.repo_path = str(git_repo.path)
        
        self.defect_prone_files = {}
        self.defect_free_files = {}

        # Get releases for repository        
        for commit in RepositoryMining(self.repo_path, only_releases=True).traverse_commits():
            self.__releases.append(commit.hash)
        
        # Get commits for repository        
        for commit in RepositoryMining(self.repo_path, only_in_branch='master').traverse_commits():
            self.__commits.append(commit.hash)


    def __has_fix_in_message(self, message: str):
        """
        Analyze a message and check whether it contains references to some fix for an issue 
        """
        fix = re.match(r'fix(e(d|s))?\s+.*\(?#\d+\)?', message.lower())
        return fix is not None

    def __set_commits_closing_issues(self):
        """ 
        Analyze a repository, and set the commits that fix some issues \
        by looking at the commit that explicitly closes or fixes those issues.
        """
        g = Git()
        for issue in g.get_issues(self.repo_name):
            
            if not issue:
                continue
            
            try:
                issue_events = issue.get_events()
                if issue_events is None or issue_events.totalCount == 0:
                    return None
                
                for e in issue_events: 
                    if e.event.lower() == 'closed' and e.commit_id:
                        self.__commits_closing_issues.add(e.commit_id)

            except ReadTimeout:
                pass                
   
    def __get_defect_prone_files(self, file: DefectiveFile):
        """
        Return the names of the file at each release within the "buggy period" [file.from_commit, file.to_commit)
        """
        for commit in RepositoryMining(self.repo_path, from_commit=file.bic_commit, to_commit=file.fix_commit, only_in_branch='master', reversed_order=True).traverse_commits():

            if commit.hash == file.fix_commit:
                continue

            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                # Handle renaming
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.old_path

            if commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

    def __get_defect_free_files(self, file: DefectiveFile):
        """
        Return the names of the file at each release within the "buggy-free period" [start-end]\[file.from_commit, file.to_commit)
        """
   
        # From file.bic_commit (i.e., bic commit) to the oldest commit
        for commit in RepositoryMining(self.repo_path, from_commit=file.bic_commit, reversed_order=True, only_in_branch='master').traverse_commits():
            
            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                # Handle renaming
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.old_path

            if commit.hash != file.bic_commit and commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

        # From file.to_commit (fixing commit) to the newest commit
        for commit in RepositoryMining(self.repo_path, from_commit=file.fix_commit, only_in_branch='master').traverse_commits():
            
            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.new_path

            if commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

    def find_defective_files(self):
       
        renamed_files = {}  # To keep track of renamed files
        defective_files = []

        for commit in RepositoryMining(self.repo_path, only_in_branch='master', reversed_order=True).traverse_commits():
            
            is_fixing_commit = self.__has_fix_in_message(commit.msg) or (commit.hash in self.__commits_closing_issues)
                        
            for modified_file in commit.modifications:
               
                # Handle renaming
                if modified_file.change_type == ModificationType.RENAME:
                    renamed_files[modified_file.old_path] = renamed_files.get(modified_file.new_path, modified_file.new_path)
                
                # Keep only files that have been modified (no renamed or deleted files)
                elif modified_file.change_type != ModificationType.MODIFY:
                    continue

                # Keep only Ansible files
                if not filters.is_ansible_file(modified_file.new_path):
                    continue

                if not is_fixing_commit:
                    break

                buggy_inducing_commits = self.repo.get_commits_last_modified_lines(commit, modified_file)
                if not buggy_inducing_commits:
                    continue
                
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
                    # older than the bic saved previously, then replace it
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
     
        for file in self.find_defective_files():

            # Get list of defect-prone files
            for commit_hash, filepath in self.__get_defect_prone_files(file):
                self.defect_prone_files.setdefault(commit_hash, set()).add(filepath)

            # Create list of defect-free files
            for commit_hash, filepath in self.__get_defect_free_files(file):
                self.defect_free_files.setdefault(commit_hash, set()).add(filepath)
