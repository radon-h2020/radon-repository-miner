import github
import json

class ContentFileEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ContentFile):
            return obj.__dict__

        elif isinstance(obj, dict):
                return obj

        return super(ContentFileEncoder, self).default(obj)


class ContentFile():

    def __init__(self, content: github.ContentFile=None):
        """
        Initialize a new content file from github.ContentFile.

        :file: a file to parse
        """

        if type(content) == dict:
            for k, v in content.items():
                setattr(self, k, v)
        else:
            self.commit_sha = None
            
            if content:
                self.sha = content.sha
                self.filename = content.path
                self.decoded_content = str(content.decoded_content.decode("utf-8"))
                self.repository = content.repository

    @property
    def is_ansible(self):
        return 'playbooks' in self.filename or 'meta' in self.filename or 'tasks' in self.filename or 'handlers' in self.filename or 'roles' in self.filename

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ContentFile):
            return self.sha == other.sha
                   
        return False
    
    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash(self.sha)