from pydriller.repository_mining import RepositoryMining
from typing import List, Union

from radonminer import filters
from radonminer.mining.base import BaseMiner


class ToscaMiner(BaseMiner):
    """
    This class extends BaseMiner to mine TOSCA-based repositories
    """

    def __init__(self, access_token: str, path_to_repo: str, host: str, full_name_or_id: Union[str, int],
                 branch: str = 'master'):
        """
        Initialize a new AnsibleMiner for a software repository.

        :param path_to_repo: the path to the repository to analyze;
        :param full_name_or_id: the repository's full name or id (e.g., radon-h2020/radon-repository-miner);
        :param branch: the branch to analyze. Default 'master';
        """
        super().__init__(access_token, path_to_repo, host, full_name_or_id, branch)

    def discard_undesired_fixing_commits(self, commits: List[str]):
        # get a sorted list of commits in ascending order of date
        self.sort_commits(commits)

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=commits[0],  # first commit in commits
                                       to_commit=commits[-1],  # last commit in commits
                                       only_in_branch=self.branch).traverse_commits():

            # if none of the modified files is a TOSCA file, then discard the commit
            if not any(filters.is_tosca_file(modified_file.new_path, modified_file.source_code) for modified_file in commit.modifications):
                if commit.hash in commits:
                    commits.remove(commit.hash)

    def ignore_file(self, path_to_file: str, content: str = None):
        return not filters.is_tosca_file(path_to_file, content)
