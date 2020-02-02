import github
import json

from enum import Enum
from requests.exceptions import ReadTimeout
from iacminer.entities.file import File, FileEncoder

class BuggyInducingCommitEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, BuggyInducingCommit):
            json_files = json.dumps(list(obj.files), cls=FileEncoder)
            json_commit = obj.__dict__
            json_commit['files'] = json.loads(json_files)

            return json_commit

        elif isinstance(obj, list):
            json_obj = []
            for item in obj:
                json_obj.append(json.dumps(item, cls=BuggyInducingCommitEncoder))

            return json_obj

        return super(BuggyInducingCommitEncoder, self).default(obj)

class BuggyInducingCommit():
   
    def __init__(self, commit: dict=None):
        """
        Initialize a new commit from github.Commit and filters out the file for the \
        specified filter.
        :commit: a commit to parse
        """

        if type(commit) == dict:
            for k, v in commit.items():
                setattr(self, k, v)
        else:
            self.from_fix = None  # Hash of the fixing commit
            self.hash = None
            self.repo = None
            self.filepaths = set()
            self.release = [] # range of commit: start release, end release
            self.repo = None
            self.date = None
            self.timezone = None

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, BuggyInducingCommit):
            return self.hash == other.hash
                   
        return False

    def __hash__(self):
        return hash(self.hash)