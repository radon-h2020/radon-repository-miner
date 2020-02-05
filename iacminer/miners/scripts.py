"""
A module for mining and downloading raw scripts.
"""
import os

from pydriller.repository_mining import GitRepository

from iacminer import filters
from iacminer.entities.content import ContentFile
from iacminer.entities.release import Release

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

    def all_files(self):
        """
        Obtain the list of the files (excluding .git directory).

        :return: the set of the files
        """
        _all = set()

        for root, _, filenames in os.walk(str(self.repo.path)):
            if '.git' in root:
                continue
            for filename in filenames: 
                path = os.path.join(root, filename)
                path = path.replace(str(self.repo.path), '')
                if path.startswith('/'):
                    path = path[1:]

                _all.add(path)

        return _all

    #def mine(self, bic: BuggyInducingCommit):
    def mine(self, release: Release):
        """ 
        Extract the content of defect-prone and unclassified files \
        from the repository at that point in time (i.e. release.end).

        :release: a release to analyze

        :return: yield tuple (content: str, defective: bool)
        """
        
        all_files = self.all_files()
        defect_prone_files = release.defective_filepaths
        unclassified_files = all_files - defect_prone_files
        
        yield_unclassified = False

        for filepath in defect_prone_files:
            if filepath in all_files:
                yield_unclassified = True
                content = self.get_file_content(filepath)
                content.defective = True
                yield content

        if not yield_unclassified:
            return

        for filepath in unclassified_files:
            if not filters.is_ansible_file(filepath):
                continue
        
            content = self.get_file_content(filepath)
            content.defective = False
            yield content
