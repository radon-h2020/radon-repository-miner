import github
import json

class FileEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, File):
            return obj.__dict__

        elif isinstance(obj, dict):
                return obj

        elif isinstance(obj, list):
            json_obj = []
            for item in obj:
                json_obj.append(json.dumps(item, cls=FileEncoder))

            return json_obj

        return super(FileEncoder, self).default(obj)

class File():

    def __init__(self, file: github.File):
        """
        Initialize a new file from github.File.

        :file: a file to parse
        """

        if type(file) == dict:
            for k, v in file.items():
                setattr(self, k, v)
        else:
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
            self.release_starts_at = None
            self.release_ends_at = None

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, File):
            return self.sha == other.sha
                   
        return False

    def __hash__(self):
        return hash(self.sha)
