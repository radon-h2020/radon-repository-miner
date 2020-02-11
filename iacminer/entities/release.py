class Release():

    def __init__(self, start: str, end: str, date: str):
        self.start = start
        self.end = end
        self.date = date

    @property
    def has_only_one_commit(self):
        return self.start == self.end

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Release):
            return self.start == other.start and self.end == other.end
                   
        return False

    def __hash__(self):
        return hash(self.start + self.end)