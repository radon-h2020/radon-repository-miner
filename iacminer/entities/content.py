import json

class ContentFileEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ContentFile):
            return obj.__dict__

        elif isinstance(obj, dict):
                return obj

        return super(ContentFileEncoder, self).default(obj)


class ContentFile():

    def __init__(self, content: dict=None):
        """
        Initialize a new content file.

        :file: a file to parse
        """

        self.commit_sha = ''
        self.sha = ''
        self.filename = ''
        self.repository = ''
        self.release_starts_at = ''
        self.release_ends_at = ''

        if type(content) == dict:
            for k, v in content.items():
                setattr(self, k, v)
     
    @property
    def is_ansible(self):
        return ('playbooks' in self.filename or 'meta' in self.filename or 'tasks' in self.filename or 'handlers' in self.filename or 'roles' in self.filename) and self.filename.endswith('.yml')

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ContentFile):
            return self.sha == other.sha
                   
        return False
    
    def __str__(self):
        return str(self.__dict__)

    def __hash__(self):
        return hash(self.sha)