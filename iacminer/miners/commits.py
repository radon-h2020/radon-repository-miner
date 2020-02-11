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
from iacminer.entities.commit import BuggyInducingCommit
from iacminer.entities.file import DefectiveFile

from iacminer.mygit import Git

class CommitsMiner():

    def __init__(self, git_repo: GitRepository):
        """
        :git_repo: a GitRepository object
        """
        self.__commits_closing_issues = set() # Set of commits sha closing issues
        self.__releases = []

        self.repo = git_repo
        owner_repo = str(git_repo.path).split('/')[1:]
        self.repo_name = f'{owner_repo[0]}/{owner_repo[1]}'
        self.repo_path = str(git_repo.path)
        
        self.defect_prone_files = {}
        self.defect_free_files = {}


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

        for commit in RepositoryMining(self.repo_path, from_commit=file.from_commit, to_commit=file.to_commit, only_in_branch='master').traverse_commits():
            
            if commit.hash == file.to_commit: # Is the fixing commit, so ignore
                break

            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                # Handle renaming
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.new_path

            if commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

    def __get_defect_free_files(self, file: DefectiveFile):
        """
        Return the names of the file at each release within the "buggy-free period" [start-end]\[file.from_commit, file.to_commit)
        """
   
        # From file.from_commit (i.e., bic commit) to the oldest commit
        for commit in RepositoryMining(self.repo_path, from_commit=file.from_commit, reversed_order=True, only_in_branch='master').traverse_commits():
            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                # Handle renaming
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.old_path

            if commit.hash != file.from_commit and commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

        # From file.to_commit (fixing commit) to the newest commit
        for commit in RepositoryMining(self.repo_path, from_commit=file.to_commit, only_in_branch='master').traverse_commits():
            
            for modified_file in commit.modifications:
                if file.filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                if modified_file.change_type == ModificationType.RENAME:
                    file.filepath = modified_file.new_path

            if commit.hash in self.__releases:
                yield (commit.hash, file.filepath)

    def find_defective_files(self):
        
        commits = []
        defective_files = []

        for commit in RepositoryMining(self.repo_path, only_in_branch='master').traverse_commits():
            
            commits.append(commit.hash)

            is_fix = self.__has_fix_in_message(commit.msg) or (commit.hash in self.__commits_closing_issues)
            
            if not is_fix:
                continue
            
            for modified_file in commit.modifications:

                # Keep only files that have been modified (no renamed or deleted files)
                if modified_file.change_type != ModificationType.MODIFY:
                    continue

                # Keep only Ansible files
                if not filters.is_ansible_file(modified_file.new_path):
                    continue
                    
                buggy_inducing_commits = self.repo.get_commits_last_modified_lines(commit, modified_file)
                    
                if not buggy_inducing_commits:
                    continue
  
                min_idx = len(commits)-1

                for hash in buggy_inducing_commits[modified_file.new_path]:
                    idx = commits.index(hash)
                    if idx >= 0 and idx < min_idx:
                        min_idx = idx
                
                # First buggy inducing commit hash
                bic_hash = commits[min_idx]

                defective_files.append(
                    DefectiveFile(modified_file.new_path, from_commit=bic_hash, to_commit=commit.hash)
                )

        return defective_files

    def mine(self):
        """ 
        Analyze a repository, yielding buggy inducing commits.
        """

        # Get releases for repository        
        for commit in RepositoryMining(self.repo_path, only_releases=True).traverse_commits():
            self.__releases.append(commit.hash)
        
        self.__set_commits_closing_issues()
     
        for file in self.find_defective_files():

            # Get list of defect-prone files
            for commit_hash, filepath in self.__get_defect_prone_files(file):
                self.defect_prone_files.setdefault(commit_hash, set()).add(filepath)


            # Create list of defect-free files
            for commit_hash, filepath in self.__get_defect_free_files(file):
                self.defect_free_files.setdefault(commit_hash, set()).add(filepath)
