import yaml

from typing import List

from pydriller.repository_mining import RepositoryMining
from pydriller.domain.commit import ModificationType

from repominer import filters, utils
from repominer.mining.ansible_modules import DATABASE_MODULES, FILE_MODULES, IDENTITY_MODULES, NETWORK_MODULES, STORAGE_MODULES
from repominer.mining.base import BaseMiner, FixingCommitClassifier

CONFIG_DATA_MODULES = DATABASE_MODULES + FILE_MODULES + IDENTITY_MODULES + NETWORK_MODULES + STORAGE_MODULES


class AnsibleMiner(BaseMiner):
    """ This class extends BaseMiner to mine Ansible-based repositories
    """

    def __init__(self, url_to_repo: str, branch: str = 'master'):
        super(self.__class__, self).__init__(url_to_repo, branch)
        self.FixingCommitClassifier = AnsibleFixingCommitClassifier

    def discard_undesired_fixing_commits(self, commits: List[str]):
        """
        Given a list of commits, discard commits that do not modify at least one Ansible file.

        Note, the update occurs in-place. That is, the original list is updated.

        Parameters
        ----------
        commits : List[str]
            List of commit hash

        """
        # get a sorted list of commits in ascending order of date
        self.sort_commits(commits)

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=commits[0],  # first commit in commits
                                       to_commit=commits[-1],  # last commit in commits
                                       only_in_branch=self.branch).traverse_commits():

            # if none of the modified files is a Ansible file, then discard the commit
            if not any(modified_file.change_type == ModificationType.MODIFY and filters.is_ansible_file(
                    modified_file.new_path) for modified_file in commit.modifications):
                if commit.hash in commits:
                    commits.remove(commit.hash)

    def get_fixing_commit_classifier(self):
        return AnsibleFixingCommitClassifier

    def ignore_file(self, path_to_file: str, content: str = None):
        """
        Ignore non-Ansible files.

        Parameters
        ----------
        path_to_file: str
            The filepath (e.g., repominer/mining/base.py).

        content: str
            The file content.

        Returns
        -------
        bool
            True if the file is not an Ansible file, and must be ignored. False, otherwise.

        """
        return not filters.is_ansible_file(path_to_file)


class AnsibleFixingCommitClassifier(FixingCommitClassifier):
    """ This class extends a FixingCommitClassifier to classify bug-fixing commits of Ansible files.
    """

    def data_changed(self) -> bool:
        for modification in self.commit.modifications:
            if modification.change_type != ModificationType.MODIFY or not filters.is_ansible_file(modification.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modification.source_code_before)
                source_code_current = yaml.safe_load(modification.source_code)

                data_before = [value for key, value in utils.key_value_list(source_code_before) if key in CONFIG_DATA_MODULES]
                data_current = [value for key, value in utils.key_value_list(source_code_current) if key in CONFIG_DATA_MODULES]

                return data_before != data_current

            except yaml.YAMLError:
                pass

        return False

    def include_changed(self) -> bool:
        for modification in self.commit.modifications:
            if modification.change_type != ModificationType.MODIFY or not filters.is_ansible_file(
                    modification.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modification.source_code_before)
                source_code_current = yaml.safe_load(modification.source_code)

                includes_before = [value for key, value in utils.key_value_list(source_code_before) if key in (
                    'include', 'include_role', 'include_tasks', 'include_vars', 'import_playbook', 'import_tasks',
                    'import_role')]
                includes_current = [value for key, value in utils.key_value_list(source_code_current) if key in (
                    'include', 'include_role', 'include_tasks', 'include_vars', 'import_playbook', 'import_tasks',
                    'import_role')]

                return includes_before != includes_current

            except yaml.YAMLError:
                pass

        return False

    def service_changed(self) -> bool:
        for modification in self.commit.modifications:
            if modification.change_type != ModificationType.MODIFY or not filters.is_ansible_file(
                    modification.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modification.source_code_before)
                source_code_current = yaml.safe_load(modification.source_code)

                services_before = [value for key, value in utils.key_value_list(source_code_before) if key == 'service']
                services_current = [value for key, value in utils.key_value_list(source_code_current) if
                                    key == 'service']

                return services_before != services_current

            except yaml.YAMLError:
                pass

        return False
