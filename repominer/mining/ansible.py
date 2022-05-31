import yaml

from typing import List

from pydriller.repository import Repository
from pydriller.domain.commit import ModificationType

from repominer import filters, utils
from repominer.mining.ansible_modules import DATABASE_MODULES, FILE_MODULES, IDENTITY_MODULES, NETWORK_MODULES, \
    STORAGE_MODULES
from repominer.mining.base import BaseMiner, FixingCommitClassifier

CONFIG_DATA_MODULES = DATABASE_MODULES + FILE_MODULES + IDENTITY_MODULES + NETWORK_MODULES + STORAGE_MODULES


class AnsibleMiner(BaseMiner):
    """ This class extends BaseMiner to mine Ansible-based repositories
    """

    def __init__(self, url_to_repo: str, clone_repo_to: str, branch: str = None):
        super(self.__class__, self).__init__(url_to_repo, clone_repo_to, branch)
        self.FixingCommitClassifier = AnsibleFixingCommitClassifier

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

    def is_data_changed(self) -> bool:
        for modified_file in self.commit.modified_files:
            if modified_file.change_type != ModificationType.MODIFY or not filters.is_ansible_file(
                    modified_file.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modified_file.source_code_before)
                source_code_current = yaml.safe_load(modified_file.source_code)

                data_before = [value for key, value in utils.key_value_list(source_code_before) if
                               key in CONFIG_DATA_MODULES]
                data_current = [value for key, value in utils.key_value_list(source_code_current) if
                                key in CONFIG_DATA_MODULES]

                return data_before != data_current

            except yaml.YAMLError:
                pass

        return False

    def is_include_changed(self) -> bool:
        for modified_file in self.commit.modified_files:
            if modified_file.change_type != ModificationType.MODIFY or not filters.is_ansible_file(
                    modified_file.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modified_file.source_code_before)
                source_code_current = yaml.safe_load(modified_file.source_code)

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

    def is_service_changed(self) -> bool:
        for modified_file in self.commit.modified_files:
            if modified_file.change_type != ModificationType.MODIFY or not filters.is_ansible_file(
                    modified_file.new_path):
                continue

            try:
                source_code_before = yaml.safe_load(modified_file.source_code_before)
                source_code_current = yaml.safe_load(modified_file.source_code)

                services_before = [value for key, value in utils.key_value_list(source_code_before) if key == 'service']
                services_current = [value for key, value in utils.key_value_list(source_code_current) if
                                    key == 'service']

                return services_before != services_current

            except yaml.YAMLError:
                pass

        return False
