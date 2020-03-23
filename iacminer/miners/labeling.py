from enum import Enum
from iacminer.entities.file import FixingFile, LabeledFile
from pydriller.repository_mining import RepositoryMining
from pydriller.domain.commit import ModificationType

class LabelingTechnique(Enum):
    """
    DEFECTIVE_FROM_OLDEST_BIC - The file is labeled "buggy" from the oldest buggy inducing commit (inclusive) to the fixing commit (exclusive), and "clean" from the start to the oldest bic .
    
    DEFECTIVE_AT_EVERY_BIC - The file is labeled "buggy" only for commits that induced bugs, and "clean" for all other commits.
    """
    DEFECTIVE_FROM_OLDEST_BIC = 1
    DEFECTIVE_AT_EVERY_BIC = 2


class AbstractLabeler():

    def __init__(self, path_to_repo: str):
        """
        Parameters
        ----------
        path_to_repo: str : path to the repository the file belongs to.
        """
        self.path_to_repo = path_to_repo

    def label(self, file: FixingFile):
        """
        Traverses the commits from the fixing commit the file belongs to,
        to the begin of the project and labels each version of the file as
        'clean' or 'buggy'.
        
        Parameters
        ----------
        file : file.FixingFile: a fixing file to analyze.

        Return
        ----------
        labeled_files : list[LabeledFile] : the list of labeled files.
        """
        list()


class LabelDefectiveFromOldestBic(AbstractLabeler):

    def label(self, files: list):
        
        files = files.copy()
        under_labeling = dict()
        labeled_files = list()

        for commit in RepositoryMining(self.path_to_repo, order='reverse').traverse_commits():

            for i in range(len(list(files)) - 1, -1, -1):
                fix = files[i]

                if fix.fic == commit.hash:
                    under_labeling[fix.fic] = fix
                    del files[i]

            finished = set()

            for fic_hash, fix in under_labeling.items():

                if not fix.bics:
                    finished.add(fic_hash)
                    continue

                if commit.hash in fix.bics:
                    fix.bics.remove(commit.hash)    

                if fix.filepath and commit.hash != fic_hash:

                    labeled_files.append(
                        LabeledFile(filepath=fix.filepath,
                                    commit=commit.hash,
                                    label=LabeledFile.Label.DEFECT_PRONE,
                                    fixing_commit=fix.fic))


                # Handle file renaming
                for modified_file in commit.modifications:

                    if not fix.filepath:
                        continue
                    
                    if fix.filepath not in (modified_file.old_path, modified_file.new_path):
                        continue
                    
                    fix.filepath = modified_file.old_path

            for hash in finished:
                del under_labeling[hash]

        return labeled_files



    """
    def label(self, file: FixingFile):
        
        labeled_files = list()

        filepath = file.filepath
        defect_prone = True
        bics = file.bics.copy()
        
        for commit in RepositoryMining(self.path_to_repo,
                                       to_commit=file.fic,
                                       order='reverse').traverse_commits():

            if not bics:
                break
            
            if commit.hash in bics:
                bics.remove(commit.hash)

            # Label current filepath
            if filepath and commit.hash != file.fic:

                if defect_prone:
                    label = LabeledFile.Label.DEFECT_PRONE
                else:
                    label = LabeledFile.Label.DEFECT_FREE

                labeled_files.append(
                    LabeledFile(filepath=filepath,
                                commit=commit.hash,
                                label=label,
                                fixing_commit=file.fic))

            # Handle file renaming
            for modified_file in commit.modifications:

                if not filepath:
                    continue
                
                if filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                filepath = modified_file.old_path
        
        return labeled_files
    """

class LabelDefectiveAtBic(AbstractLabeler):

    def label(self, file: FixingFile):
        
        labeled_files = list()

        filepath = file.filepath

        for commit in RepositoryMining(self.path_to_repo,
                                       to_commit=file.fic,
                                       order='reverse').traverse_commits():

            if not filepath:
                break

            elif filepath and commit.hash != file.fic:
                # Label current filepath

                if commit.hash in file.bics:
                    label = LabeledFile.Label.DEFECT_PRONE
                else:
                    label = LabeledFile.Label.DEFECT_FREE

                labeled_files.append(
                    LabeledFile(filepath=filepath,
                                commit=commit.hash,
                                label=label,
                                fixing_commit=file.fic))
                
            # Handle file renaming
            for modified_file in commit.modifications:
                
                if not filepath:
                    continue
                
                if filepath not in (modified_file.old_path, modified_file.new_path):
                    continue
                
                if modified_file.change_type == ModificationType.ADD:
                        filepath = None
                else:
                    filepath = modified_file.old_path
            
        return labeled_files