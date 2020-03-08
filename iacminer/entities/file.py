from enum import Enum

class FixingFile():

    def __init__(self, filepath: str, bic_commit: str, fix_commit: str):
        self.filepath = filepath  # Name at FIXING COMMIT
        self.bic_commit = bic_commit
        self.fix_commit = fix_commit

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, FixingFile):
            return self.filepath == other.filepath
                   
        return False

    def __str__(self):
        return str(self.__dict__)

class LabeledFile():
    """
    This class is responsible to implement the methods for storing information
    about labeled files
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
                 ref: str):
        """
        Initialize a new labeled file
        
        Parameters
        ----------
        filepath : str: the path of the file
        
        commit : str : the hash of the commit the file belongs to

        label : str : the label for the file (i.e., 'defect-prone', 'defect-free')

        ref : str : the reference to the original file (to group different versions \
            of files with different names, but being the same file)
        """

        self.filepath = filepath
        self.commit = commit
        self.label = label
        self.ref = ref