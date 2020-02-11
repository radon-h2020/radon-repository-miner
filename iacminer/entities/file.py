class DefectiveFile():

    def __init__(self, filepath: str, from_commit: str, to_commit: str):
        self.filepath = filepath
        self.from_commit = from_commit
        self.to_commit = to_commit