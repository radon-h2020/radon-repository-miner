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


class CommitsMiner():

    def __init__(self, git_repo: GitRepository):
        """
        :git_repo: a GitRepository object
        """
        self.repo = git_repo
        
        owner_repo = str(git_repo.path).split('/')[1:]
        self.repo_name = f'{owner_repo[0]}/{owner_repo[1]}'
        self.repo_path = str(git_repo.path)

        self.__releases = []
        self.__release_dates = {}
        self.__commits_closing_issues = set() # Set of commits sha closing issues

        self.buggy_inducing_commits = list()

    def __has_fix_in_message(self, message: str):
        """
        Analyze a message and check whether it contains references to some fix for an issue 
        """
        fix = re.match(r'fix(e(d|s))?\s+.*\(?#\d+\)?', message.lower())
        return fix is not None

    def __set_buggy_inducing_commits(self):
        """
        Analyze a repository, and return the buggy inducing commits.
        :return: Generator 
        """
        release = {}
        date = {}
        is_first_release_commit = True

        for commit in RepositoryMining(self.repo_path, only_in_branch='master').traverse_commits():
            
            date[commit.hash] = {'date': commit.committer_date}

            # Handle release period information
            if is_first_release_commit:
                is_first_release_commit = False
                from_commit_sha = commit.hash

            release[commit.hash] = {
                'starts_at': from_commit_sha,
                'ends_at': self.__releases[0] if len(self.__releases) else None
            }

            if commit.hash in self.__releases:
                # Count next commit as starting from the new release period
                is_first_release_commit = True
                self.__releases.pop(0)
            
            # Skip if not fix (but after handling renaming)
            is_fix = self.__has_fix_in_message(commit.msg)

            """
            if not is_fix and commit.hash not in self.__commits_closing_issues:
                continue
            """
            for modified_file in commit.modifications:
                
                # Filter out non Ansible files
                if not filters.is_ansible_file(modified_file.new_path):
                    continue

                # Keep only files that have been modified
                if modified_file.change_type != ModificationType.MODIFY:
                    continue

                if not is_fix:
                    continue

                # Find buggy inducing commits
                files = {}
                buggy_inducing_commits = self.repo.get_commits_last_modified_lines(commit, modified_file)

                for filepath, commit_hashes in buggy_inducing_commits.items():
                    for hash in commit_hashes:
                        files.setdefault(hash, set()).add(filepath)

                for buggy_commit_hash, filenames in files.items():
                    bic = BuggyInducingCommit()
                    bic.hash = buggy_commit_hash 

                    if bic not in self.buggy_inducing_commits:
                        bic.filepaths = filenames
                        bic.date = date[buggy_commit_hash]['date']
                        bic.repo = self.repo_name
                        bic.release = [
                            release.get(buggy_commit_hash, {}).get('starts_at', None),
                            release.get(buggy_commit_hash, {}).get('ends_at', None)
                        ]
                        bic.release_date = self.__release_dates.get(bic.release_ends_at, None)

                        if not bic.release_date:
                            continue
                        
                        self.buggy_inducing_commits.append(bic)
                    else:
                        idx = self.buggy_inducing_commits.index(bic)
                        bic = self.buggy_inducing_commits[idx]
                        bic.filepaths = bic.filepaths.union(filenames)

    def __handle_renamed_files(self):
        for bic in self.buggy_inducing_commits:

            # Handle renaming from fix commit to buggy inducing commit
            for commit in RepositoryMining(self.repo_path, from_commit=bic.hash, reversed_order=True, only_in_branch='master').traverse_commits():
                
                if commit.hash == bic.hash:
                    break

                for modified_file in commit.modifications:
                    if modified_file.change_type == ModificationType.RENAME and modified_file.new_path in bic.filepaths:
                        bic.filepaths.remove(modified_file.new_path)
                        bic.filepaths.add(modified_file.old_path)

            # Handle renaming from buggy inducing commit to release commit
            bic.release_filepaths = bic.filepaths

            for commit in RepositoryMining(self.repo_path, from_commit=bic.hash, to_commit=bic.release_ends_at, only_in_branch='master').traverse_commits():
                
                for modified_file in commit.modifications:
                    if modified_file.change_type == ModificationType.RENAME and modified_file.old_path in bic.release_filepaths:
                        bic.release_filepaths.remove(modified_file.old_path)
                        bic.release_filepaths.add(modified_file.new_path)
                    elif modified_file.change_type == ModificationType.DELETE and modified_file.old_path in bic.release_filepaths:
                        bic.release_filepaths.remove(modified_file.old_path)
                
                if commit.hash == bic.release_ends_at:
                    break
    
    def mine(self):
        """ 
        Analyze a repository, yielding buggy inducing commits.
        """

        # Get releases for repository        
        for commit in RepositoryMining(self.repo_path, only_releases=True).traverse_commits():
            self.__releases.append(commit.hash)
            self.__release_dates[commit.hash] = commit.committer_date

        self.__set_buggy_inducing_commits()
        self.__handle_renamed_files()
        
        return self.buggy_inducing_commits 
