from pydriller.repository import Repository
from pydriller.domain.commit import ModificationType

from typing import List

from repominer import filters
from repominer.mining.base import BaseMiner


class ToscaMiner(BaseMiner):
    """ This class extends the BaseMiner to mine TOSCA-based repositories
    """

    def discard_undesired_fixing_commits(self, commits: List[str]):
        """
        Given a list of commits, discard commits that do not modify at least one Tosca file.

        Note, the update occurs in-place. That is, the original list is updated.

        Parameters
        ----------
        commits : List[str]
            List of commit hash

        """
        # get a sorted list of commits in ascending order of date
        self.sort_commits(commits)

        for commit in Repository(self.path_to_repo,
                                 from_commit=commits[0],  # first commit in commits
                                 to_commit=commits[-1],  # last commit in commits
                                 only_in_branch=self.branch).traverse_commits():

            # if none of the modified files is a TOSCA file, then discard the commit
            if not any(modified_file.change_type == ModificationType.MODIFY and filters.is_tosca_file(modified_file.new_path, modified_file.source_code)
                       for modified_file in commit.modified_files):
                if commit.hash in commits:
                    commits.remove(commit.hash)

    def ignore_file(self, path_to_file: str, content: str = None):
        """
        Ignore non-TOSCA files.

        Parameters
        ----------
        path_to_file: str
            The filepath (e.g., repominer/mining/base.py).

        content: str
            The file content.

        Returns
        -------
        bool
            True if the file is not a TOSCA file, and must be ignored. False, otherwise.

        """
        return not filters.is_tosca_file(path_to_file, content)
