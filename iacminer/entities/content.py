import github

class ContentFile():

    def __init__(self, content: github.ContentFile=None):
        """
        Initialize a new content file from github.ContentFile.

        :file: a file to parse
        """
        self.__commit_sha = None
        
        if content:
            self.__sha = content.sha
            self.__filename = content.path
            self.__decoded_content = content.decoded_content
            self.__repository = content.repository

    @property
    def commit_sha(self):
        return self.__commit_sha

    @commit_sha.setter
    def commit_sha(self, value: str):
        self.__commit_sha = value
        
    @property
    def sha(self):
        return self.__sha

    @sha.setter
    def sha(self, value: str):
        self.__sha = value
        
    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value: str):
        self.__filename = value

    @property
    def decoded_content(self):
        return self.__decoded_content

    @decoded_content.setter
    def decoded_content(self, value: str):
        self.__decoded_content = value

    @property
    def repository(self):
        return self.__repository

    @repository.setter
    def repository(self, value: str):
        self.__repository = value

    @property
    def is_ansible(self):
        return 'playbooks' in self.filename or 'meta' in self.filename or 'tasks' in self.filename or 'handlers' in self.filename or 'roles' in self.filename

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ContentFile):
            return self.sha == other.sha
                   
        return False
    
    def __hash__(self):
        return hash(self.__sha)