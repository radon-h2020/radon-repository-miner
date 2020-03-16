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

    def __init__(self, name, labeler: int=1, language: str='ansible'):
        
        self.name = name
        self.language = language
        self.path_to_repo = join('/tmp/', self.name)

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

    def start(self):
        
        self.clone_repo()

        git_repo = GitRepository(self.path_to_repo)
        metrics_miner = MetricsMiner()
        repo_miner = RepositoryMiner(self.path_to_repo)
        labeled_files = repo_miner.mine(self.labeler)
        
        if not labeled_files:
            return

        # Extract metrics (per commit)
        for commit in RepositoryMining(self.path_to_repo).traverse_commits():         

            try:
                # TODO: Gestire caso per release attualmente implementato in main.py
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

                if not content:
                    print(f'>>> Commit: {commit.hash}. File not found')
                    continue

                try:
                    iac_metrics = metrics_miner.mine_product_metrics(content)
                except YAMLError:
                    print(f'>>> Commit: {commit.hash}. Cannot properly read the yaml file!')
                    continue
                except ValueError:
                    print(f'>>> Commit: {commit.hash}. Value error in yaml!')
                    continue

                tokens = metrics_miner.mine_text(content)

                metrics = iac_metrics

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

        self.delete_repo()
