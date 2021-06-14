import unittest

from repominer.mining.ansible import AnsibleFixingCommitClassifier
from pydriller.repository import Repository

URL_TO_REPO = 'https://github.com/stefanodallapalma/radon-repository-miner-testing'
BRANCH = 'origin/test-ansible-commit-classifier'


class AnsibleFixingCommitClassifierTestSuite(unittest.TestCase):

    # def test_fixes_configuration_data(self):
    #
    #     for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH, only_commits=COMMITS).traverse_commits():
    #         print(commit.hash)
    #         if commit.hash in ('d6a21546e4b211f6499fc4fb0db3b79496aa4ccc',):
    #             self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_configuration_data())
    #         else:
    #             self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_configuration_data())

    # def test_fixes_dependency(self):
    #
    #     for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH).traverse_commits():
    #         if commit.hash in ('859185c33e97d053e3bc61020ddc7ee51cb19fd8',):
    #             self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_dependency())
    #         else:
    #             self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_dependency())

    # def test_fixes_service(self):
    #
    #     for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH).traverse_commits():
    #         if commit.hash in ('fbf7bf44032c3b216abccf52faf788e129a90314',):
    #             self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_service())
    #         else:
    #             self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_service())

    def test_fixes_idempotency(self):
        for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH).traverse_commits():
            if commit.hash in ('3de3d8c2bbccf62ef5698cf33ad258aae5316432',):
                # This is the initial commit. Change the message for testing purpose only
                commit._c_object.message = 'Fix task \'primary-swift-proxy\' idempotency.'
                self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_idempotency())
            else:
                self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_idempotency())

    def test_fixes_security(self):
        for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH).traverse_commits():
            if commit.hash in ('3de3d8c2bbccf62ef5698cf33ad258aae5316432',):
                # This is the initial commit. Change the message for testing purpose only
                commit._c_object.message = 'Fixes keystone token after deploying keystone to minimize security risk.'
                self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_security())
            else:
                self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_security())

    def test_fixes_syntax(self):
        for commit in Repository(path_to_repo=URL_TO_REPO, only_in_branch=BRANCH).traverse_commits():
            if commit.hash in ('3de3d8c2bbccf62ef5698cf33ad258aae5316432',):
                # This is the initial commit. Change the message for testing purpose only
                commit._c_object.message = 'Fix Ansible Linter issues.'
                self.assertTrue(AnsibleFixingCommitClassifier(commit).fixes_syntax())
            else:
                self.assertFalse(AnsibleFixingCommitClassifier(commit).fixes_syntax())
