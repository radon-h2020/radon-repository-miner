import unittest

from repominer import utils


class UtilsTestSuite(unittest.TestCase):

    @staticmethod
    def test_get_dependents():
        sentence = 'fix wrong condit when check the statu of mysqladmin that caus the output to be both in the case ' \
                   'of success and failur of mysqladmin ping command '
        assert utils.get_head_dependents(sentence) == ['fix', 'condit', 'statu', 'output']

    @staticmethod
    def test_get_dependents_empty():
        assert not utils.get_head_dependents('')

    @staticmethod
    def test_key_value_list_continue():
        dict1 = {'key': None}
        dict2 = {None: 'value'}

        assert len(utils.key_value_list(dict1)) == 0
        assert len(utils.key_value_list(dict2)) == 0
