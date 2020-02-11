class BuggyInducingCommit():
   
    def __init__(self):
        """
        Initialize a new buggy inducing commit
        """

        self.hash = None
        self.repo = None
        self.filepaths = set() # are the names of the fixed files in buggy inducing commits
        self.release_filepaths = set()  # are the names of the fixed files in the release commit. 
        self.release = [] # range of commit: start release, end release
        self.release_date = None
        self.repo = None
        self.date = None
        self.fixed_at = None
        self.fix_period = [] # range of commit: start release, end release
        self.fix_filepaths = set()  # are the names of the fixed files in the release commit. 

    @property
    def release_starts_at(self):
        return self.release[0]

    @property
    def release_ends_at(self):
        return self.release[1]

    
    @property
    def fix_starts_at(self):
        return self.fix_period[0]

    @property
    def fix_ends_at(self):
        return self.fix_period[1]


    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, BuggyInducingCommit):
            return self.hash == other.hash
                   
        return False

    def __hash__(self):
        return hash(self.hash)