"""
A module for mining repositories.
"""
import github
import json
import os

from pydriller.domain.commit import ModificationType
from pydriller.repository_mining import GitRepository, RepositoryMining

from iacminer import filters
from iacminer.entities.file import FixingFile, LabeledFile

from iacminer.mygit import Git

from dotenv import load_dotenv
load_dotenv()

# Constants
BUG_RELATED_LABELS = set(['bug', 'Bug', 'bug :bug:', 'ansible_bug', 'Type: Bug', 'Type: bug',
                          'type: bug 🐛', 'type:bug', 'type: bug', 'kind/bug', 'kind/bugs',
                          'bugfix', 'critical-bug', '01 type: bug', 'bug_report', 'minor-bug'])

class RepositoryMiner():  
    """
    This class is responsible for mining a repository.
    """

    def __init__(self, path_to_repo: str, branch: str='master'):
        """
        Initialize a new miner for a software repository.
        
        Parameters
        ----------
        path_to_repo : the path to the repository to analyze;

        branch : the git branch to analyze. Default None.
        """ 

        self.path_to_repo = path_to_repo
        self.branch = branch

        self.commits_hash = [c.hash for c in RepositoryMining(self.path_to_repo, only_in_branch=self.branch).traverse_commits()]
        self.fixing_commits = set()

    def set_fixing_commits(self):
        """
        Set commits that have fixed closed bug-related issues
        """ 
        g = Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        base, name = os.path.split(self.path_to_repo)
        _, owner = os.path.split(base)
        remote_repo = f'{owner}/{name}'

        # Get all the labels in the repository
        labels = g.get_labels(remote_repo)
        
        # Keep only the labels related to a bug
        labels = BUG_RELATED_LABELS.intersection(labels)
        
        # Get all the issues with labels related to a bug
        issues = list()
        
        for label in labels:
            issues.extend(g.get_closed_issues(remote_repo, label))

        for issue in issues:
            issue_events = issue.get_events()

            if not issue_events or issue_events.totalCount == 0:
                return None
            
            for e in issue_events: 
                is_merged = e.event.lower() == 'merged'
                is_closed = e.event.lower() == 'closed'

                if (is_merged or is_closed) and e.commit_id:
                    self.fixing_commits.add(e.commit_id)

    def get_fixing_files(self):
        """
        Find files fixing issues related to bug.

        Return
        -------

        fixing_files : set : the list of files.
        """
        fixing_files = list()

        # Order fixing commits
        sorted_fixing_commits = [hash for hash in self.commits_hash if hash in list(self.fixing_commits)]
        
        if not sorted_fixing_commits:
            return list()

        first_fix, last_fix = sorted_fixing_commits[0], sorted_fixing_commits[-1]
        renamed_files = dict()
        git_repo = GitRepository(self.path_to_repo)


        for commit in RepositoryMining(self.path_to_repo, 
                                       from_commit=last_fix,
                                       to_commit=first_fix,
                                       reversed_order=True,
                                       only_in_branch=self.branch).traverse_commits():
            
            # If no Ansible file modified, go to next iteration
            if not any(filters.is_ansible_file(modified_file.new_path) for modified_file in commit.modifications):
                if commit.hash in self.fixing_commits:
                    self.fixing_commits.remove(commit.hash)
                
                continue
            
            # Find buggy inducing commits
            for modified_file in commit.modifications:
                
                # Not interested that are ADDED or DELETED
                if modified_file.change_type not in (ModificationType.MODIFY, ModificationType.RENAME):
                    continue

                if modified_file.change_type == ModificationType.RENAME:

                    if modified_file.new_path in renamed_files:
                        renamed_files[modified_file.old_path] = renamed_files[modified_file.new_path]

                    elif commit.hash in self.fixing_commits:
                        renamed_files[modified_file.old_path] = modified_file.new_path
                
                if commit.hash not in self.fixing_commits:
                    continue

                buggy_inducing_commits = git_repo.get_commits_last_modified_lines(commit, modified_file)
                
                if not buggy_inducing_commits:
                    continue
                
                # Get the index of the oldest commit among those that induced the bug
                min_idx = len(self.commits_hash)-1
                for hash in buggy_inducing_commits[modified_file.new_path]:
                    idx = self.commits_hash.index(hash)
                    if idx < min_idx:
                        min_idx = idx
                
                # First buggy inducing commit hash
                oldest_bic_hash = self.commits_hash[min_idx]

                fixing_file = FixingFile(renamed_files.get(modified_file.new_path, modified_file.new_path),
                                   bic_commit=oldest_bic_hash,
                                   fix_commit=commit.hash)

                try:
                    # Get defective file
                    idx = fixing_files.index(fixing_file)
                    fixing_file = fixing_files[idx]

                    # If the oldest buggy inducing commit found in the previous step is 
                    # older than a bic saved previously, then replace it
                    idx = self.commits_hash.index(fixing_file.bic_commit)
                    if min_idx < idx:  
                        fixing_file.bic_commit = oldest_bic_hash  

                except ValueError: # fixing file not yet in the list
                    fixing_files.append(fixing_file)

        return fixing_files
   
    def label_file(self, file: FixingFile):
        """
        Traverses the commits from the fixing commit the file belongs to,
        to the begin of the project and labels each version of the file as
        'defect-free' or 'defect-prone' depending on whether the versionof
        the file belongs to a commit before or later the buggy inducing commit,
        respectively.
        
        Parameters
        ----------
        file : file.FixingFile: a fixing file to analyze.

        Return
        ----------
        labeled_versions : list : the list of all versions of the file labeled as 'defect-free' or 'defect-prone'.
        """

        labeled_versions = list()

        filepath = file.filepath
        defect_prone = True

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=self.commits_hash[0],
                                       to_commit=file.fix_commit,
                                       reversed_order=True,
                                       only_in_branch=self.branch).traverse_commits():

            # Label current filepath
            if filepath and commit.hash != file.fix_commit:

                label = LabeledFile.Label.DEFECT_FREE

                if defect_prone:
                    label = LabeledFile.Label.DEFECT_PRONE

                labeled_versions.append(
                    LabeledFile(filepath=filepath,
                        commit=commit.hash,
                        label=label,
                        ref=file.filepath))

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
        
        return labeled_versions

    def mine(self):
        """
        Start mining the repository.
        
        Return
        ----------
        labeled_files : list : the list of labeled files (i.e., defect-prone or defect-free), if any.
        """

        self.set_fixing_commits()
        
        labeled_files = list()

        if self.fixing_commits:
            for file in self.get_fixing_files():
                labeled_files.extend(self.label_file(file))

        return labeled_files
