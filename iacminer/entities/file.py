class DefectiveFile():

    def __init__(self, filepath: str, bic_commit: str, fix_commit: str, ):
        self.filepath = filepath  # Name at FIXING COMMIT
        self.bic_commit = bic_commit
        self.fix_commit = fix_commit

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, DefectiveFile):
            return self.filepath == other.filepath
                   
        return False

    def __str__(self):
        return str(self.__dict__)