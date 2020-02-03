class BuggyInducingCommit():
   
    def __init__(self):
        """
        Initialize a new buggy inducing commit
        """

        self.hash = None
        self.repo = None
        self.filepaths = set()
        self.release = [] # range of commit: start release, end release
        self.repo = None
        self.date = None

    @property
    def release_starts_at(self):
        return self.release[0]

    @property
    def release_ends_at(self):
        return self.release[1]

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, BuggyInducingCommit):
            return self.hash == other.hash
                   
        return False

    def __hash__(self):
        return hash(self.hash)