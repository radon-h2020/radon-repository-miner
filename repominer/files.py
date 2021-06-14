import json
from dataclasses import dataclass


class FixedFileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FixedFile):
            return {
                "filepath": o.filepath,
                "fic": o.fic,
                "bic": o.bic
            }


class FixedFileDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.to_object, *args, **kwargs)

    def to_object(self, o):
        if type(o) == dict:
            return FixedFile(filepath=o["filepath"],
                             fic=o["fic"],
                             bic=o["bic"])


@dataclass
class FixedFile:
    """ This class stores information about fixed files (i.e., files modified by fixing commits)

    Attributes
    ----------
    filepath : str
        The file of the path at the bug-fixing commit
    fic : str
        The bug-fixing commit sha
    bic : str
        The bug-introducing commit sha

    """

    filepath: str
    fic: str
    bic: str

    def __eq__(self, other):
        if isinstance(other, FixedFile):
            return self.filepath == other.filepath

        return False


class FailureProneFileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FailureProneFile):
            return {
                "filepath": o.filepath,
                "commit": o.commit,
                "fixing_commit": o.fixing_commit
            }


class FailureProneFileDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.to_object, *args, **kwargs)

    def to_object(self, o):
        if type(o) == dict:
            return FailureProneFile(filepath=o["filepath"],
                                    commit=o["commit"],
                                    fixing_commit=o["fixing_commit"])


@dataclass
class FailureProneFile:
    """ This class stores information about failure prone files

    Attributes
    ----------
    filepath : str
        The filepath relative to the repository's root
    commit : str
        The commit sha
    fixing_commit : str
        The bug-fixing commit sha

    """

    filepath: str
    commit: str
    fixing_commit: str

    def __eq__(self, other):
        if isinstance(other, FailureProneFile):
            return self.filepath == other.filepath and self.commit == other.commit

        return False
