from pydriller.repository_mining import RepositoryMining
from pydriller.domain.commit import ModificationType

from typing import List

from repominer import filters
from repominer.mining.base import BaseMiner


class ToscaMiner(BaseMiner):
    """
    This class extends BaseMiner to mine TOSCA-based repositories
    """

    def __init__(self, url_to_repo: str, branch: str = 'master'):
        """
        Initialize a new ToscaMiner for a software repository.

        :param url_to_repo: the path to the repository to analyze;
        :param branch: the branch to analyze. Default 'master';
        """
        super().__init__(url_to_repo, branch)

    def discard_undesired_fixing_commits(self, commits: List[str]):
        # get a sorted list of commits in ascending order of date
        self.sort_commits(commits)

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=commits[0],  # first commit in commits
                                       to_commit=commits[-1],  # last commit in commits
                                       only_in_branch=self.branch).traverse_commits():

            # if none of the modified files is a TOSCA file, then discard the commit
            if not any(modified_file.change_type == ModificationType.MODIFY and filters.is_tosca_file(modified_file.new_path, modified_file.source_code) for modified_file in commit.modifications):
                if commit.hash in commits:
                    commits.remove(commit.hash)

    def ignore_file(self, path_to_file: str, content: str = None):
        return not filters.is_tosca_file(path_to_file, content)
