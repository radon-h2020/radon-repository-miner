from enum import Enum

class FixingFile():

    def __init__(self, filepath: str, bics: set, fix_commit: str):
        self.filepath = filepath  # Name at FIXING COMMIT
        self.bics = bics
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
                 fixing_filepath: str,
                 fixing_commit: str):
        """
        Initialize a new labeled file
        
        Parameters
        ----------
        filepath : str: the path of the file
        
        commit : str : the hash of the commit the file belongs to

        label : str : the label for the file (i.e., 'defect-prone', 'defect-free')

        fixing_filepath : str : the name of the file at fixing commit (to group different versions \
            of files with different names, but being the same file)
        
        fixing_commit : str : the commit fixing this file 
        """

        self.filepath = filepath
        self.commit = commit
        self.label = label
        self.fixing_filepath = fixing_filepath
        self.fixing_commit = fixing_commit

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, LabeledFile):
            return self.filepath == other.filepath and self.commit == other.commit

        return False