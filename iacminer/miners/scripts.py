"""
A module for mining and downloading raw scripts.
"""
import os

from pydriller.repository_mining import GitRepository

from iacminer import filters
from iacminer.entities.content import ContentFile
from iacminer.entities.commit import BuggyInducingCommit

class ScriptsMiner():

    def __init__(self, git_repo: GitRepository):
        """
        :git_repo: a GitRepository object
        """
        self.repo = git_repo

    def get_file_content(self, filepath):
        with open(os.path.join(self.repo.path, filepath), 'r') as f:
            content = ContentFile(
                filepath = filepath,
                content = f.read()
            )

            return content

    def files(self):
        """
        Obtain the list of the files (excluding .git directory).

        :return: the set of the files
        """
        _all = set()
        for path, _, files in os.walk(str(self.repo.path)):
            if '.git' in path:
                continue
            for name in files:
                path = path.replace(str(self.repo.path), '')
                path = os.path.join(path, name)
                if path[0] == '/':
                    path = path[1:] 
                _all.add(path)
        return _all

    def mine(self, bic: BuggyInducingCommit):
        """ 
        Extract the content of defect-prone and unclassified files \
        from the repository at that point in time (i.e. bic.hash).

        :bic: a buggy inducing commit to analyze

        :return: yield tuple (content: str, defective: bool)
        """
        
        # Checkout to bic.hash to retrieve file contents
        self.repo.checkout(bic.hash)
        defect_prone_files = bic.filepaths
        unclassified_files = self.files() - bic.filepaths
        
        for filepath in defect_prone_files:
            content = self.get_file_content(filepath)
            content.defective = True
            yield content

        for filepath in unclassified_files:
            if not filters.is_ansible_file(filepath):
                continue
        
            content = self.get_file_content(filepath)
            content.defective = False
            yield content
