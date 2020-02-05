class Release():

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.defective_filepaths = set()
        self.repo = ''
        self.date = ''
        self.buggy_inducing_commits = set()
        
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Release):
            return self.start == other.start and self.end == other.end
                   
        return False

    def __hash__(self):
        return hash(self.start + self.end)