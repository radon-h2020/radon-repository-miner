import git
import shutil

from os import makedirs, walk
from os.path import isfile, isdir, join

from datetime import timedelta
from datetime import datetime
from iacminer import filters
from iacminer import utils
from iacminer.entities.file import LabeledFile
from iacminer.miners.labeling import LabelingTechnique
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.repository import RepositoryMiner
from pydriller import GitRepository, RepositoryMining
from pydriller.domain.commit import ModificationType
from yaml.error import YAMLError

class MineRepo():

    def __init__(self, name, labeler: int=1, language: str='ansible', branch:str='master'):
        
        self.name = name
        self.language = language
        self.path_to_repo = join('/tmp/', self.name)
        self.default_branch = branch
        
        if labeler == 1:
            self.labeler = LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC
        elif labeler == 2:
            self.labeler = LabelingTechnique.DEFECTIVE_AT_EVERY_BIC
        else:
            self.labeler = LabelingTechnique.DEFECTIVE_AT_EVERY_BIC


    def all_files(self):
        """
        Get the set of all the files in the repository (excluding .git directory).
        
        Return
        ----------
        files : set : the set of strings (filepaths).
        """

        files = set()

        for root, _, filenames in walk(self.path_to_repo):
            if '.git' in root:
                continue
            for filename in filenames: 
                path = join(root, filename)
                path = path.replace(self.path_to_repo, '')
                if path.startswith('/'):
                    path = path[1:]

                files.add(path)

        return files

    def clone_repo(self):
        """
        Clone a repository on the local machine.
        
        Parameters
        ----------
        owner : str : the name of the owner of the repository.

        name : str : the name of the repository.
        """
        path_to_owner = join('/tmp/', self.name.split('/')[0])

        if not isdir(path_to_owner):
            makedirs(path_to_owner)
            git.Git(path_to_owner).clone(f'https://github.com/{self.name}.git')

    def delete_repo(self):
        """
        Delete a local repository.
        
        Parameters
        ----------
        owner : str : the name of the owner of the repository.
        """

        path_to_owner = join('/tmp/', self.name.split('/')[0])
        try:
            shutil.rmtree(path_to_owner)
        except Exception as e:
            print(f'>>> Error while deleting directory: {str(e)}')

    def get_content(self, path):
        """
        Get the content of a file as plain text.
        
        Parameters
        ----------
        path : str : the path to the file.

        Return
        ----------
        str : the content of the file, if exists; None otherwise.
        """
        if not isfile(path):
            return None

        with open(path, 'r') as f:
            return f.read()

    def mine_per_release(self):
        git_repo = GitRepository(self.path_to_repo)
        metrics_miner = MetricsMiner()
        repo_miner = RepositoryMiner(self.path_to_repo, self.default_branch)
        labeled_files = repo_miner.mine(self.labeler)

        if not labeled_files:
            return

        utils.save_fixing_commits(self.name, repo_miner.fixing_commits)

        # Group labeled files per release
        commit_file_map = dict()
        for file in labeled_files:
            if not filters.is_ansible_file(file.filepath):
                    continue
            
            commit_file_map.setdefault(file.commit, list()).append(file)

        # Extract metrics
        releases = [c.hash for c in RepositoryMining(self.path_to_repo, only_releases=True).traverse_commits()]

        last_release_date = None

        metrics_miner = MetricsMiner()
        iac_metrics_before = dict() # Values for iac metrics in the last release

        path_when_added = dict()

        for commit in RepositoryMining(self.path_to_repo).traverse_commits():

            # To handle renaming in iac_metrics_before
            for modified_file in commit.modifications:
                
                old_path = modified_file.old_path
                new_path = modified_file.new_path
               
                if old_path in path_when_added:
                    path_when_added[new_path] = path_when_added.pop(old_path)
                else:
                    path_when_added[new_path] = new_path

                if old_path != new_path and old_path in iac_metrics_before:
                    # Rename key old_path wit new_path
                    iac_metrics_before[new_path] = iac_metrics_before.pop(old_path)
                
            if not last_release_date:
                last_release_date = commit.committer_date

            if commit.hash not in releases:
                continue
            
            # PROCESS metrics
            process_metrics = metrics_miner.mine_process_metrics(self.path_to_repo, since=last_release_date + timedelta(minutes=1), to=commit.committer_date)

            last_release_date = commit.committer_date

            # Checkout to commit to extract product metrics from each file
            git_repo.checkout(commit.hash)
            
            # IAC metrics
            all_filepaths = self.all_files()
            labeled_this_commit = commit_file_map.get(commit.hash, [])

            defect_prone = all_filepaths.intersection([file.filepath for file in labeled_this_commit if file.label == LabeledFile.Label.DEFECT_PRONE])
            defect_free = all_filepaths - defect_prone

            # Uncommented: Consider only releases having at least one defect files. 
            # Comment: Consider all the releases
            if not defect_prone:
                continue

            for filepath in defect_free.union(defect_prone):
                
                if not filters.is_ansible_file(filepath):
                    continue

                # Compute product and text metrics
                content = self.get_content(join(self.path_to_repo, filepath))

                try:
                    iac_metrics = metrics_miner.mine_product_metrics(content)
                except YAMLError:
                    label = "defect-prone" if filepath in defect_prone else "defect-free"
                    print(f'>>> Commit: {commit.hash} - Cannot properly {filepath} - The file label is {label}.')
                    continue
                except ValueError: # Content is empty
                    continue

                # TOKENS
                tokens = metrics_miner.mine_text(content)

                # DELTA metrics
                delta_metrics = dict()

                previous = iac_metrics_before.get(filepath, dict())
                for k, v in previous.items():
                    v_delta = iac_metrics.get(k, 0) - v
                    delta_metrics[f'delta_{k}'] = round(v_delta, 3)

                iac_metrics_before[filepath] = iac_metrics.copy()

                metrics = iac_metrics
                metrics.update(delta_metrics)

                # Getting process metrics for the specific filepath
                metrics['change_set_max'] = process_metrics[0]
                metrics['change_set_avg'] = process_metrics[1]
                metrics['code_churn'] = process_metrics[2].get(filepath, 0)
                metrics['code_churn_max'] = process_metrics[3].get(filepath, 0)
                metrics['code_churn_avg'] = process_metrics[4].get(filepath, 0)
                metrics['commits_count'] = process_metrics[5].get(filepath, 0)
                metrics['contributors'] = process_metrics[6].get(filepath, 0)
                metrics['minor_contributors'] = process_metrics[7].get(filepath, 0)
                metrics['highest_experience'] = process_metrics[8].get(filepath, 0)
                metrics['median_hunks_count'] = process_metrics[9].get(filepath, 0)
                metrics['loc_added'] = process_metrics[10].get(filepath, 0)
                metrics['loc_added_max'] = process_metrics[11].get(filepath, 0)
                metrics['loc_added_avg'] = process_metrics[12].get(filepath, 0)
                metrics['loc_removed'] = process_metrics[13].get(filepath, 0)
                metrics['loc_removed_max'] = process_metrics[14].get(filepath, 0)
                metrics['loc_removed_avg'] = process_metrics[15].get(filepath, 0)

                metrics.update(
                    dict(commit=commit.hash,    # release commit
                         committed_at=datetime.timestamp(commit.committer_date), # release date
                         defective = 1 if filepath in defect_prone else 0,
                         filepath=filepath,
                         repo=self.name,
                         path_when_added = path_when_added.get(filepath, 'NA'),
                         tokens=' '.join(tokens))
                )

                yield metrics

            git_repo.reset()    # Reset repository's status

    def mine_per_commit(self):
        metrics_miner = MetricsMiner()
        repo_miner = RepositoryMiner(self.path_to_repo, self.default_branch)
        labeled_files = repo_miner.mine(self.labeler)
        
        if not labeled_files:
            return
        
        # Extract metrics (per commit)
        for commit in RepositoryMining(self.path_to_repo).traverse_commits():         

            try:
                process_metrics = metrics_miner.mine_process_metrics(self.path_to_repo,
                                                                     from_commit=commit.hash,
                                                                     to_commit=commit.hash)
            except Exception as e:
                print(f'>>> Problem with process metrics: {str(e)}')
                continue

            for modified_file in commit.modifications:
                
                filepath = modified_file.new_path

                if self.language == 'ansible' and not filters.is_ansible_file(filepath):
                    continue

                # Compute product and text metrics
                content = modified_file.source_code
                content_before = modified_file.source_code_before

                if not content:
                    continue
                
                # IAC METRICS
                iac_metrics = dict()
                iac_metrics_before = dict()
                delta_metrics = dict()
                
                try:
                    iac_metrics = metrics_miner.mine_product_metrics(content)

                    if content_before:
                        iac_metrics_before = metrics_miner.mine_product_metrics(content_before)

                        # delta
                        for k in iac_metrics.keys():
                            if k in iac_metrics_before:
                                k_delta = f'delta_{k}'
                                v_delta = iac_metrics.get(k, 0) - iac_metrics_before.get(k, 0)
                                delta_metrics[k_delta] = round(v_delta, 3)
                
                except YAMLError:
                    print(f'>>> Commit: {commit.hash}. Cannot properly read the content of: {filepath}!')
                    #continue
                except ValueError as ve: # Content is empty
                    continue
                
                # TOKENS
                tokens = metrics_miner.mine_text(content)

                # DELTA metrics
                delta_metrics = dict()
                metrics = iac_metrics
                metrics.update(delta_metrics)

                # Getting process metrics for the specific filepath
                metrics['change_set_max'] = process_metrics[0]
                metrics['change_set_avg'] = process_metrics[1]
                metrics['code_churn'] = process_metrics[2].get(filepath, 0)
                metrics['code_churn_max'] = process_metrics[3].get(filepath, 0)
                metrics['code_churn_avg'] = process_metrics[4].get(filepath, 0)
                metrics['commits_count'] = process_metrics[5].get(filepath, 0)
                metrics['contributors'] = process_metrics[6].get(filepath, 0)
                metrics['minor_contributors'] = process_metrics[7].get(filepath, 0)
                metrics['highest_experience'] = process_metrics[8].get(filepath, 0)
                metrics['median_hunks_count'] = process_metrics[9].get(filepath, 0)
                metrics['loc_added'] = process_metrics[10].get(filepath, 0)
                metrics['loc_added_max'] = process_metrics[11].get(filepath, 0)
                metrics['loc_added_avg'] = process_metrics[12].get(filepath, 0)
                metrics['loc_removed'] = process_metrics[13].get(filepath, 0)
                metrics['loc_removed_max'] = process_metrics[14].get(filepath, 0)
                metrics['loc_removed_avg'] = process_metrics[15].get(filepath, 0)

                metrics.update(
                    dict(commit=commit.hash,
                         committed_at=datetime.timestamp(commit.committer_date),
                         defective='yes' if LabeledFile(modified_file.new_path, commit.hash, None, None, None) in labeled_files else 'no',
                         filepath=filepath,
                         repo=self.name,
                         tokens=' '.join(tokens))
                )

                yield metrics

    def start(self):
        
        self.clone_repo()

        if self.labeler == LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC:
            for metric in self.mine_per_release():
                yield metric

        elif self.labeler == LabelingTechnique.DEFECTIVE_AT_EVERY_BIC:
            for metric in self.mine_per_commit():
                yield metric     

        self.delete_repo()
