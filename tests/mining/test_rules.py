import unittest

from repominer.mining import rules


class RulesTestCase(unittest.TestCase):

    @staticmethod
    def test_has_defect_pattern_true():
        assert rules.has_defect_pattern('fix wrong package dependency for Debian/Ubuntu')

    @staticmethod
    def test_has_defect_pattern_false():
        assert not rules.has_defect_pattern('refactored code')

    @staticmethod
    def test_has_conditional_pattern_true():
        assert rules.has_conditional_pattern('fix wrong condition in foo.yml')

    @staticmethod
    def test_has_conditional_pattern_false():
        assert not rules.has_conditional_pattern('refactored code')

    @staticmethod
    def test_has_storage_configuration_pattern_true():
        assert rules.has_storage_configuration_pattern('Fix sql query')

    @staticmethod
    def test_has_storage_configuration_pattern_false():
        assert not rules.has_storage_configuration_pattern('refactored code')

    @staticmethod
    def test_has_file_configuration_pattern_true():
        assert rules.has_file_configuration_pattern('fix permission to file by adding explicit mode')

    @staticmethod
    def test_has_file_configuration_pattern_false():
        assert not rules.has_file_configuration_pattern('refactored code')

    @staticmethod
    def test_has_network_configuration_pattern_true():
        assert rules.has_network_configuration_pattern('fix ip address binding')

    @staticmethod
    def test_has_network_configuration_pattern_false():
        assert not rules.has_network_configuration_pattern('refactored code')

    @staticmethod
    def test_has_user_configuration_pattern_true():
        assert rules.has_user_configuration_pattern('removed hard-coded string password')

    @staticmethod
    def test_has_user_configuration_pattern_false():
        assert not rules.has_user_configuration_pattern('refactored code')

    @staticmethod
    def test_has_cache_configuration_pattern_true():
        assert rules.has_cache_configuration_pattern('Delete cache after task execution')

    @staticmethod
    def test_has_cache_configuration_pattern_false():
        assert not rules.has_cache_configuration_pattern('refactored code')

    @staticmethod
    def test_has_dependency_pattern_true():
        assert rules.has_dependency_pattern('fix wrong package dependency for Debian/Ubuntu')

    @staticmethod
    def test_has_dependency_pattern_false():
        assert not rules.has_dependency_pattern('refactored code')

    @staticmethod
    def test_has_documentation_pattern_true():
        assert rules.has_documentation_pattern('Updated readme and specifications')

    @staticmethod
    def test_has_documentation_pattern_false():
        assert not rules.has_documentation_pattern('refactored code')

    @staticmethod
    def test_has_idempotency_pattern_true():
        assert rules.has_idempotency_pattern('Fix task primary-swift-proxy idempotency.')

    @staticmethod
    def test_has_idempotency_pattern_false():
        assert not rules.has_idempotency_pattern('refactored code')

    @staticmethod
    def test_has_security_pattern_true():
        assert rules.has_security_pattern('Deletes keystone token after deploying keystone to minimize security risk')

    @staticmethod
    def test_has_security_pattern_false():
        assert not rules.has_security_pattern('refactored code')

    @staticmethod
    def test_has_service_pattern_true():
        assert rules.has_service_pattern('Fix Upstart service issues')

    @staticmethod
    def test_has_service_pattern_false():
        assert not rules.has_service_pattern('refactored code')

    @staticmethod
    def test_has_syntax_pattern_true():
        assert rules.has_syntax_pattern('Fix lint issue')

    @staticmethod
    def test_has_syntax_pattern_false():
        assert not rules.has_syntax_pattern('refactored code')

    @staticmethod
    def test_get_dependents():
        sentence = 'fix wrong condit when check the statu of mysqladmin that caus the output to be both in the case of success and failur of mysqladmin ping command'
        assert rules.get_head_dependents(sentence) == ['fix', 'condit', 'statu', 'output']

    @staticmethod
    def test_get_dependents_empty():
        assert not rules.get_head_dependents('')


from repominer.mining.rules import FixingCommitCategorizer
from pydriller.repository_mining import RepositoryMining


class FixingCommitCategorizerTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Create a fake pydriller.commit.Commit for test
        cls.commit_obj = list(RepositoryMining(path_to_repo='https://github.com/stefanodallapalma/test-github-apis',
                                       only_commits=['c9ada15de53d048f4d8e74d12bea62174bc0f957']).traverse_commits())[0]

    def test_fixes_conditional(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix wrong conditional when checking the status of mysqladmin ' \
                                                       'that caused the output to be  0, both in the case of success ' \
                                                       'and failure of mysqladmin’s ‘ping’ command. Fixed that in ' \
                                                       'the new version. '
        fcc = FixingCommitCategorizer(commit)
        assert fcc.fixes_conditional()
        assert not fcc.fixes_dependency()
        assert not fcc.fixes_documentation()
        assert not fcc.fixes_idempotency()
        assert not fcc.fixes_security()
        assert not fcc.fixes_configuration_data()
        assert not fcc.fixes_service()
        assert not fcc.fixes_syntax()

    def test_fixes_idempotency(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix task \'primary-swift-proxy\' idempotency.'
        fcc = FixingCommitCategorizer(commit)
        assert fcc.fixes_idempotency()
        assert not fcc.fixes_conditional()
        assert not fcc.fixes_dependency()
        assert not fcc.fixes_documentation()
        assert not fcc.fixes_security()
        assert not fcc.fixes_configuration_data()
        assert not fcc.fixes_service()
        assert not fcc.fixes_syntax()

    def test_fixes_security(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fixes keystone token after deploying keystone to minimize security risk.'
        fcc = FixingCommitCategorizer(commit)
        assert not fcc.fixes_conditional()
        assert not fcc.fixes_dependency()
        assert not fcc.fixes_documentation()
        assert not fcc.fixes_idempotency()
        assert fcc.fixes_security()
        assert not fcc.fixes_configuration_data()
        assert not fcc.fixes_service()
        assert not fcc.fixes_syntax()

    def test_fixes_syntax(self):
        commit = self.commit_obj
        commit._c_object.message = 'Fix Ansible Linter issues'
        fcc = FixingCommitCategorizer(commit)
        assert not fcc.fixes_conditional()
        assert not fcc.fixes_dependency()
        assert not fcc.fixes_documentation()
        assert not fcc.fixes_idempotency()
        assert not fcc.fixes_security()
        assert not fcc.fixes_configuration_data()
        assert not fcc.fixes_service()
        assert fcc.fixes_syntax()
