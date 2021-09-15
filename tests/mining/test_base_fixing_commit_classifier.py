import copy
import unittest

from repominer.mining.base import FixingCommitClassifier
from pydriller.repository import Repository


class BaseFixingCommitClassifierTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.commit = list(copy.deepcopy(commit) for commit in Repository(
            path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
            only_commits=['3de3d8c2bbccf62ef5698cf33ad258aae5316432']
        ).traverse_commits())[0]

    def test_init__type_error(self):
        with self.assertRaises(TypeError):
            FixingCommitClassifier(commit=None)

    def test_init__sentence(self):
        classifier = FixingCommitClassifier(self.commit)
        self.assertEqual(classifier.sentences, [['Initial', 'commit']])

    def test_is_data_changed__abstract(self):
        fcc = FixingCommitClassifier(self.commit)
        self.assertFalse(fcc.is_data_changed())
        self.assertFalse(fcc.is_include_changed())
        self.assertFalse(fcc.is_service_changed())

    def test_fixes_config_data(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_configuration_data())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'Fix user permissions'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_configuration_data())

        commit_tmp._c_object.message = 'Fix ip address'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_configuration_data())

        commit_tmp._c_object.message = 'Fix username login service'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_configuration_data())

        commit_tmp._c_object.message = 'Fixed cache problem'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_configuration_data())

    def test_fixes_dependency(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_dependency())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'fix wrong package dependency for Debian/Ubuntu'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_dependency())

    def test_fixes_docs_false(self):
        for commit in Repository(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                 only_commits=['3de3d8c2bbccf62ef5698cf33ad258aae5316432',
                                               'ea49aab402a7cb64e9382e764f202d9e6c8f4cbe',
                                               'd39fdb44e98869835fe59a86d20d05a9e82d5282']).traverse_commits():

            if commit.hash == '3de3d8c2bbccf62ef5698cf33ad258aae5316432':
                self.assertFalse(FixingCommitClassifier(commit).fixes_documentation())
                self.assertFalse(FixingCommitClassifier(commit).is_comment_changed())

            elif commit.hash == 'ea49aab402a7cb64e9382e764f202d9e6c8f4cbe':
                self.assertTrue(FixingCommitClassifier(commit).fixes_documentation())

            elif commit.hash == 'd39fdb44e98869835fe59a86d20d05a9e82d5282':
                self.assertTrue(FixingCommitClassifier(commit).is_comment_changed())

    def test_fixes_service(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_service())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'Fix nginx service that did not started the server.'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_service())

    def test_fixes_syntax(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_syntax())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'Fix Ansible Linter issues.'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_syntax())

    def test_fixes_idempotency(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_idempotency())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'Fix task \'primary-swift-proxy\' idempotency.'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_idempotency())

    def test_fixes_security(self):
        self.assertFalse(FixingCommitClassifier(self.commit).fixes_security())

        commit_tmp = copy.deepcopy(self.commit)
        commit_tmp._c_object.message = 'Fixes keystone token after deploying keystone to minimize security risk.'
        self.assertTrue(FixingCommitClassifier(commit_tmp).fixes_security())
