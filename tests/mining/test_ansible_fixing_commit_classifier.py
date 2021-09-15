import unittest

from repominer.mining.ansible import AnsibleFixingCommitClassifier
from pydriller.repository import Repository

URL_TO_REPO = 'https://github.com/stefanodallapalma/radon-repository-miner-testing'
BRANCH = 'origin/test-ansible-miner'


class AnsibleFixingCommitClassifierTestSuite(unittest.TestCase):

    def test_is_data_include_and_service_changed__false(self):

        commits = ['9cbfa528b26f1d222b1b7954eef41f55d2026f4b',  # Ansible file but not modified
                   'e14240d8ca0ffd3ca8f093f39111d048819ab909',  # File modified but not Ansible
                   'd07ed2f58c7cbabee89dbc60a62036f22c23394a']  # Modified Ansible with syntax error

        for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH, only_commits=commits).traverse_commits():
            self.assertFalse(AnsibleFixingCommitClassifier(commit).is_data_changed())
            self.assertFalse(AnsibleFixingCommitClassifier(commit).is_include_changed())
            self.assertFalse(AnsibleFixingCommitClassifier(commit).is_service_changed())
