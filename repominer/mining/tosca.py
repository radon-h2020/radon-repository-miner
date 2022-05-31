from pydriller.repository import Repository
from pydriller.domain.commit import ModificationType

from typing import List

from repominer import filters
from repominer.mining.base import BaseMiner


class ToscaMiner(BaseMiner):
    """ This class extends the BaseMiner to mine TOSCA-based repositories
    """

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
