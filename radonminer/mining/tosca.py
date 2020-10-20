from typing import List, Union
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
        raise NotImplementedError

    def ignore_file(self, path_to_file):
        raise NotImplementedError
