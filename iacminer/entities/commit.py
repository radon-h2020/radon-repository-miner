import github
import json

from enum import Enum
from iacminer.entities.file import File

class CommitEncoder(json.JSONEncoder):
    def __tojson(self, obj):
        json_files = []
        for f in obj.files:
            json_files.append(f.tojson())
        
        json_commit = obj.__dict__
        json_commit['files'] = json_files

        return json_commit


    def default(self, obj):
        if isinstance(obj, Commit):
            return self.__tojson(obj)
            
        elif isinstance(obj, list):
            json_obj = []
            for item in obj:
                json_obj.append(json.dumps(item, cls=CommitEncoder))

            return json_obj

        return super(CommitEncoder, self).default(obj)

"""
class CommitDecoder(json.JSONDecoder):
    
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):

        print(obj)

        c = Commit(None)
        c.repo = obj['repo']
        c.author_id = obj['author_id']
        c.author_name = obj['author_name']
        c.committer_id = obj['committer_id']
        c.committer_name = obj['committer_name']
        c.committer_email = obj['committer_email']
        c.message = obj['message']
        c.sha = obj['sha']
        c.url = obj['url']
        #TODO files and parents
        if type == 'datetime':
            return c

        return obj
"""

class Filter(Enum):
    ANSIBLE = 1

class Commit():
   
    def __init__(self, commit: github.Commit = None, filter: Filter = None):
        """
        Initialize a new commit from github.Commit and filters out the file for the \
        specified filter.

        :commit: a commit to parse
        :filter: a filter to filter out undesired files. \
            Can be None (default no filters), ANSIBLE (keeps only Ansible files).

        """

        if type(commit) == dict:
            for k, v in commit.items():
                setattr(self, k, v)
        else:
            self.repo = None

            if commit:
                self.author_id = commit.author.node_id if commit.author else None
                self.author_name = commit.commit.author.name if commit.commit.author else None
                self.committer_id = commit.committer.node_id if commit.committer else None
                self.committer_name = commit.commit.committer.name if commit.commit.committer else None
                self.committer_email = commit.commit.committer.email if commit.commit.committer else None
                self.message = commit.commit.message
                self.sha = commit.sha
                self.url = commit.url
                
                self.parents = []
                for c in commit.parents:
                    self.parents.append(c.sha)

                self.files = set()
                for file in commit.files:
                    if file.status == 'added' or file.status == 'removed': # Skip files created or removed at commit time
                        continue

                    if filter == Filter.ANSIBLE and not self.__is_ansible_file(file.filename):
                        continue

                    self.files.add(File(file))

    def __is_ansible_file(self, filepath: str) -> bool:
        """ 
        Return True if the file is supposed to be an Ansible file, False otherwise

        :filepath: the path of the file to analyze

        :return: bool True if filepath is of an Ansible file; False otherwise
        """
        return ('playbooks' in filepath or 'meta' in filepath or 'tasks' in filepath or 'handlers' in filepath or 'roles' in filepath) and filepath.endswith('.yml')

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Commit):
            return self.sha == other.sha
                   
        return False

    def __hash__(self):
        return hash(self.sha)

    def __str__(self):
        return str(self.__dict__)