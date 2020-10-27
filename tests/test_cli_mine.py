# !/usr/bin/python
# coding=utf-8

import os
import shutil
import unittest


class CLIMineTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)
        os.environ["TMP_REPOSITORIES_DIR"] = cls.path_to_tmp_dir

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)
        del os.environ["TMP_REPOSITORIES_DIR"]

    def test_mine(self):
        result = os.system('repo-miner mine github ansible adriagalin/ansible.motd {}'.format(self.path_to_tmp_dir))
        assert result == 0
        assert 'failure-prone-files.html' in os.listdir(self.path_to_tmp_dir)
        assert 'failure-prone-files.json' in os.listdir(self.path_to_tmp_dir)


if __name__ == '__main__':
    unittest.main()
