import github

class File():

    def __init__(self, file: github.File):
        """
        Initialize a new file from github.File.

        :file: a file to parse
        """
        self.sha = file.sha
        self.filename = file.filename
        self.previous_filename = file.previous_filename
        self.additions = file.additions
        self.deletions = file.deletions
        self.changes = file.changes
        self.blob_url = file.blob_url
        self.raw_url = file.raw_url
        self.status = file.status
        self.patch = file.patch

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, File):
            return self.sha == other.sha
                   
        return False
        