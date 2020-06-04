from enum import Enum


class FixingFile:
    """
    This class is responsible to implement the methods for storing information about fixing files (i.e., files belonging
    to fixing commits)
    """

    def __init__(self, filepath: str, bics: set, fic: str):
        """

        :param filepath: the file of the path at the fixing-commit
        :param bics: a list of sha of the bug-inducing commits
        :param fic: the sha of the fixing-commit
        """
        self.filepath = filepath  # Name at FIXING COMMIT
        self.bics = bics
        self.fic = fic

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
        Type of Label. Can be DEFECT_FREE or DEFECT_PRONE.
        """
        DEFECT_FREE = 'defect-free'
        DEFECT_PRONE = 'defect-prone'

    def __init__(self,
                 filepath: str,
                 commit: str,
                 label: Label,
                 fixing_commit: str):
        """

        :param filepath: the path of the file
        :param commit: the sha of the commit the file belongs to
        :param label: the label for the file (i.e., 'defect-prone', 'defect-free')
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
