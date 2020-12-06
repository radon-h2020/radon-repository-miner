import os
import unittest

from repominer.mining.ansible import AnsibleFixingCommitClassifier
from pydriller.repository_mining import RepositoryMining


class AnsibleFixingCommitClassifierTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Create a fake pydriller.commit.Commit for test
        cls.commit_obj = list(RepositoryMining(path_to_repo='https://github.com/stefanodallapalma/test-github-apis',
                                               only_commits=[
                                                   'c9ada15de53d048f4d8e74d12bea62174bc0f957']).traverse_commits())[0]

    @staticmethod
    def test_comment_changed_true():
        commit = list(RepositoryMining(path_to_repo=os.path.join(os.getcwd(), 'test_data', 'repositories', 'COLARepo'),
                                       only_commits=['c95685de3a5832b6beb109e283aab9db02eef620']).traverse_commits())[0]
        assert AnsibleFixingCommitClassifier(commit).comment_changed()

    @staticmethod
    def test_comment_changed_false():
        commit = list(RepositoryMining(path_to_repo=os.path.join(os.getcwd(), 'test_data', 'repositories', 'COLARepo'),
                                       only_commits=['7bf9b3acf9f3440a79b087e4433f6bd38b61a633']).traverse_commits())[0]
        fcc = AnsibleFixingCommitClassifier(commit)
        assert not fcc.comment_changed()
    @staticmethod
    def test_service_changed():
        for commit in RepositoryMining(path_to_repo='https://github.com/usableprivacy/upribox/',
                                       only_commits=['7836e5adeecbb97e9fafb5024e378efdec394764']).traverse_commits():
            assert AnsibleFixingCommitClassifier(commit).service_changed()

    @staticmethod
    def test_include_changed():
        for commit in RepositoryMining(path_to_repo='https://github.com/iiab/iiab/',
                                       only_commits=['31de9459bc7af6790fa0a3f6804eb617aca921ba',
                                                     '27428d27779b86558ac1eb7225165da180f1bcb5']).traverse_commits():
            assert AnsibleFixingCommitClassifier(commit).include_changed()


    @staticmethod
    def test_data_changed():
        for commit in RepositoryMining(path_to_repo='https://github.com/iiab/iiab/',
                                       only_commits=['9272b34b196d9010679157e493e775edca1daa13',
                                                     '25702f4e1d39965b54dec0e48bda18e8225e01d7']).traverse_commits():
            assert AnsibleFixingCommitClassifier(commit).data_changed()

    def test_fixes_conditional(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix wrong conditional when checking the status of mysqladmin ' \
                                   'that caused the output to be  0, both in the case of success ' \
                                   'and failure of mysqladmin’s ‘ping’ command. Fixed that in ' \
                                   'the new version. '
        assert AnsibleFixingCommitClassifier(commit).fixes_conditional()

    @staticmethod
    def test_fixes_configuration_data():
        for commit in RepositoryMining(path_to_repo='https://github.com/iiab/iiab/',
                                       only_commits=['25702f4e1d39965b54dec0e48bda18e8225e01d7']).traverse_commits():
            assert AnsibleFixingCommitClassifier(commit).fixes_configuration_data()

    @staticmethod
    def test_fixes_dependency():
        for commit in RepositoryMining(path_to_repo='https://github.com/iiab/iiab/',
                                       only_commits=['31de9459bc7af6790fa0a3f6804eb617aca921ba',
                                                     '27428d27779b86558ac1eb7225165da180f1bcb5']).traverse_commits():
            commit._c_object.message = 'fix include_tasks'
            assert AnsibleFixingCommitClassifier(commit).fixes_dependency()

    @staticmethod
    def test_fixes_documentation():
        commit = list(RepositoryMining(path_to_repo=os.path.join(os.getcwd(), 'test_data', 'repositories', 'COLARepo'),
                                       only_commits=['c95685de3a5832b6beb109e283aab9db02eef620']).traverse_commits())[0]
        commit._c_object.message = 'modification command line dataavenue & update incorrect comments blank topology '
        fcc = AnsibleFixingCommitClassifier(commit)
        assert fcc.fixes_documentation()

    def test_fixes_idempotency(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix task \'primary-swift-proxy\' idempotency.'
        fcc = AnsibleFixingCommitClassifier(commit)
        assert fcc.fixes_idempotency()

    def test_fixes_security(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fixes keystone token after deploying keystone to minimize security risk.'
        fcc = AnsibleFixingCommitClassifier(commit)
        assert fcc.fixes_security()

    @staticmethod
    def test_fixes_service():
        for commit in RepositoryMining(path_to_repo='https://github.com/iiab/iiab/',
                                       only_commits=['e7872a2a9da875e47e29c4bb21771c12104cd68e']).traverse_commits():

            assert AnsibleFixingCommitClassifier(commit).fixes_service()
    
    def test_fixes_syntax(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix Ansible Linter issues'
        fcc = AnsibleFixingCommitClassifier(commit)
        assert fcc.fixes_syntax()

