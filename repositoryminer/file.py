from enum import Enum
import json


class LabeledFileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, LabeledFile):
            return {
                "filepath": o.filepath,
                "commit": o.commit,
                "label": 'clean' if o.label == LabeledFile.Label.CLEAN else 'failure-prone',
                "fixing_commit": o.fixing_commit
            }

        return json.JSONEncoder.default(self, o)


class FixingFile:
    """
    This class is responsible to implement the methods for storing information about fixing files (i.e., files belonging
    to fixing commits)
    """

    def __init__(self, filepath: str, fic: str, bic: str):
        """
        :param filepath: the file of the path at the fixing-commit
        :param fic: the fixing-commit sha
        :param bic: the bug-inducing-commit sha
        """
        self.filepath = filepath  # Name at FIXING-COMMIT
        self.fic = fic
        self.bic = bic

    def __eq__(self, other):
        if isinstance(other, FixingFile):
            return self.filepath == other.filepath

        return False


class LabeledFile:
    """
    This class is responsible to implement the methods for storing information about labeled files
    """

    class Label(Enum):
        """
        Type of Label. Can be CLEAN or FAILURE_PRONE.
        """
        CLEAN = 'clean'
        FAILURE_PRONE = 'failure-prone'

    def __init__(self,
                 filepath: str,
                 commit: str,
                 label: Label,
                 fixing_commit: str):
        """
        :param filepath: the filepath from the root of the repository
        :param commit: the commit hash
        :param label: the file label (i.e., 'failure-prone' or 'clean'). Currently, only failure-prone files are returned
        :param fixing_commit: the commit fixing this file
        """

        self.filepath = filepath
        self.commit = commit
        self.label = label
        self.fixing_commit = fixing_commit

    def __eq__(self, other):
        if isinstance(other, LabeledFile):
            return self.filepath == other.filepath and self.commit == other.commit

        return False
