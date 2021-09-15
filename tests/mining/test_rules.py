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
        assert rules.has_documentation_pattern('Updated documentation')
        assert rules.has_documentation_pattern('Updated docs')
        assert rules.has_documentation_pattern('Fixed docs')
        assert rules.has_documentation_pattern('Fixed doc')

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
