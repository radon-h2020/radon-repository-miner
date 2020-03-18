import git
import shutil

from os import makedirs, walk
from os.path import isfile, isdir, join

from datetime import datetime
from iacminer import filters
from iacminer.entities.file import LabeledFile
from iacminer.miners.labeling import LabelingTechnique
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.repository import RepositoryMiner
from pydriller import GitRepository, RepositoryMining
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
        
        # Group labeled files per release
        commit_file_map = dict()
        for file in labeled_files:
            if not filters.is_ansible_file(file.filepath):
                    continue
            
            commit_file_map.setdefault(file.commit, list()).append(file)

        # Extract metrics
        releases = [c.hash for c in RepositoryMining(self.path_to_repo, only_releases=True).traverse_commits()]

        release_starts_at = None
        
        metrics_miner = MetricsMiner()
        last_iac_metrics = dict() # Store the last iac metrics for each file

        for commit in RepositoryMining(self.path_to_repo).traverse_commits():

            if not release_starts_at:
                release_starts_at = commit.hash

            if commit.hash not in releases:
                continue
            
            # PROCESS metrics
            try:
                process_metrics = metrics_miner.mine_process_metrics(self.path_to_repo, release_starts_at, commit.hash)
            except Exception as e:
                print(f'Problem with process metrics: {str(e)}')
                continue

            # Checkout to commit to extract product metrics from each file
            git_repo.checkout(commit.hash)
            
            for labeled_file in commit_file_map.get(commit.hash, []):
                
                filepath = labeled_file.filepath

                # Compute product and text metrics
                content = self.get_content(join(self.path_to_repo, filepath))

                if not content:
                    print(f'>>> Commit: {commit.hash}. File {filepath} not found')
                    continue
                
                # IAC-oriented metrics
                try:
                    iac_metrics = metrics_miner.mine_product_metrics(content)
                except YAMLError:
                    print(f'>>> Commit: {commit.hash}. Cannot properly read the yaml file!')
                    continue
                except ValueError:
                    print(f'>>> Commit: {commit.hash}. Value error in yaml!')
                    continue

                # TOKENS
                tokens = metrics_miner.mine_text(content)
                
                # DELTA metrics
                delta_metrics = dict()

                if labeled_file.fixing_filepath in last_iac_metrics:
                    # Compute delta metrics
                    last = last_iac_metrics[labeled_file.fixing_filepath]
                    for k, v in iac_metrics.items():
                        k_delta = f'delta_{k}'
                        v_delta = v - last[k]
                        delta_metrics[k_delta] = round(v_delta, 3)

                last_iac_metrics[labeled_file.fixing_filepath] = iac_metrics

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
                         defective='yes' if labeled_file.label == LabeledFile.Label.DEFECT_PRONE else 'no',
                         filepath=filepath,
                         fixing_filepath=labeled_file.fixing_filepath,
                         fixing_commit=labeled_file.fixing_commit,
                         repo=self.name,
                         release_end=commit.hash,
                         release_start=release_starts_at,
                         tokens=' '.join(tokens))
                )

                yield metrics

            release_starts_at = None # So the next commit will be the start for the successive release
            git_repo.reset()    # Reset repository's status


    def mine_per_commit(self):
        git_repo = GitRepository(self.path_to_repo)
        metrics_miner = MetricsMiner()
        repo_miner = RepositoryMiner(self.path_to_repo, self.default_branch)
        labeled_files = repo_miner.mine(self.labeler)
        
        if not labeled_files:
            return
        
        last_iac_metrics = dict() # Store the last iac metrics for each file

        # Extract metrics (per commit)
        for commit in RepositoryMining(self.path_to_repo).traverse_commits():         

            try:
                process_metrics = metrics_miner.mine_process_metrics(self.path_to_repo, commit.hash, commit.hash)
            except Exception as e:
                print(f'>>> Problem with process metrics: {str(e)}')
                continue

            git_repo.checkout(commit.hash)

            for modified_file in commit.modifications:
                
                filepath = modified_file.new_path

                if self.language == 'ansible' and not filters.is_ansible_file(filepath):
                    continue

                # Compute product and text metrics
                content = self.get_content(join(self.path_to_repo, filepath))
                # No need to cehckout: Content = modified_file.src 

                if not content:
                    print(f'>>> Commit: {commit.hash}. File not found')
                    continue
                
                # IAC METRICS
                try:
                    iac_metrics = metrics_miner.mine_product_metrics(content)
                except YAMLError:
                    print(f'>>> Commit: {commit.hash}. Cannot properly read the yaml file {filepath}!')
                    iac_metrics = dict()
                    #continue
                except ValueError as ve: # Should be empty
                    print(f'>>> Commit: {commit.hash}. Value error in {filepath}! -> {str(ve)} ')
                    continue
                
                # TOKENS
                tokens = metrics_miner.mine_text(content)

                # DELTA metrics
                delta_metrics = dict()

                if modified_file.old_path in last_iac_metrics and iac_metrics:
                    # Compute delta metrics
                    last = last_iac_metrics[modified_file.old_path]
                    for k, v in iac_metrics.items():
                        k_delta = f'delta_{k}'
                        v_delta = v - last.get(k, 0)
                        delta_metrics[k_delta] = round(v_delta, 3)

                    del last_iac_metrics[modified_file.old_path]
                
                if iac_metrics:
                    last_iac_metrics[modified_file.new_path] = iac_metrics

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

            git_repo.reset()    # Reset repository's status

    def start(self):
        
        self.clone_repo()

        if self.labeler == LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC:
            for metric in self.mine_per_release():
                yield metric

        elif self.labeler == LabelingTechnique.DEFECTIVE_AT_EVERY_BIC:
            for metric in self.mine_per_commit():
                yield metric     

        self.delete_repo()
