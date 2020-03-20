"""
A module for mining repositories.
"""
import github
import json
import os
import re

from pydriller.domain.commit import ModificationType
from pydriller.repository_mining import GitRepository, RepositoryMining

from iacminer import filters
from iacminer.entities.file import FixingFile, LabeledFile
from iacminer.miners.labeling import LabelingTechnique, AbstractLabeler, LabelDefectiveFromOldestBic, LabelDefectiveAtBic
from iacminer.mygit import Git

from dotenv import load_dotenv
load_dotenv()

# Constants
BUG_RELATED_LABELS = set(['bug', 'Bug', 'bug :bug:', 'Bug - Medium', 'Bug - Low', 'Bug - Critical',
                          'ansible_bug', 'Type: Bug', 'Type: bug', 'Type/Bug',
                          'type: bug 🐛', 'type:bug', 'type: bug', 'type/bug', 'kind/bug', 'kind/bugs',
                          'bug/bugfix', 'bugfix', 'critical-bug', '01 type: bug', 'bug_report', 'minor-bug'])

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

    def linked_issue_num(self, msg: str):
        """
        Analyze a message and return the linked issue identifier, if any; None otherwise.
        """
        if not msg:
            return None

        fixes = re.match(r'fix(e(d|s))?\s+.*\(?#(\b\d+\b)\)?', msg.lower())
        closes = re.match(r'closes\s+.*\(?#(\b\d+\b)\)?', msg.lower())
        resolves = re.match(r'resolves\s+.*\(?#(\b\d+\b)\)?', msg.lower())

        if fixes and len(fixes.groups()) > 2:
            return int(fixes.groups()[2])
        elif closes and len(closes.groups()) > 0:
            return int(closes.groups()[0])
        elif resolves and len(resolves.groups()) > 0:
            return int(resolves.groups()[0])
        
        return None
        
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

        # Iterate commits and find for those fixing/closing an issue
        # but that are not found with the previous step
        for commit in RepositoryMining(self.path_to_repo,
                                       only_in_branch=self.branch).traverse_commits():
            
            if commit.hash in self.fixing_commits:
                continue

            issue_num = self.linked_issue_num(commit.msg)
            if not issue_num:
                continue
            
            issue_labels = g.get_issue_labels(remote_repo, issue_num)

            if any(l in labels for l in issue_labels):
                self.fixing_commits.add(commit.hash)
                #print(issue_labels)
                #print(commit.msg)


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
                                       order='reverse',
                                       only_in_branch=self.branch).traverse_commits():

            # If no Ansible file modified, go to next iteration - TODO: gestire linguaggio
            if not any(filters.is_ansible_file(modified_file.new_path) for modified_file in commit.modifications):
                if commit.hash in self.fixing_commits:
                    self.fixing_commits.remove(commit.hash)

                continue
            
            #if len(commit.modifications) > 1:
            #    continue

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

                fixing_file = FixingFile(
                                   renamed_files.get(modified_file.new_path, modified_file.new_path),
                                   bics=buggy_inducing_commits[modified_file.new_path],
                                   fix_commit=commit.hash)

                if fixing_file in fixing_files:
                    # Update existinig fixing file
                    idx = fixing_files.index(fixing_file)
                    fixing_files[idx].bics.update(buggy_inducing_commits[modified_file.new_path])
                else:
                    fixing_files.append(fixing_file)

        return fixing_files

    def mine(self, labeling: LabelingTechnique):
        """
        Start mining the repository.

        Parameters
        -----------
        labeling : labeling.LabelingTechnique : the labeling technique to label files.\
            Can be DEFECTIVE_FROM_OLDEST_BIC or DEFECTIVE_AT_EVERY_BIC

        Return
        ----------
        labeled_files : list : the list of labeled files (i.e., defect-prone or defect-free), if any.
        """

        self.set_fixing_commits()
        
        labeled_files = list()

        if self.fixing_commits:
            
            if labeling == LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC:
                labeler = LabelDefectiveFromOldestBic(self.path_to_repo)
            elif labeling == LabelingTechnique.DEFECTIVE_AT_EVERY_BIC:
                labeler = LabelDefectiveAtBic(self.path_to_repo)
            else:
                labeler = AbstractLabeler(self.path_to_repo)

            for file in self.get_fixing_files():
                labeled_files.extend(labeler.label(file))

        return labeled_files
