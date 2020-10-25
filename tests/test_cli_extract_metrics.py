# !/usr/bin/python
# coding=utf-8

import os
import shutil
import unittest


class CLIExtractMetricsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_repo = os.path.join(os.getcwd(), 'test_data', 'repositories', 'ansible.motd')
        cls.path_to_report = os.path.join(os.getcwd(), 'test_data', 'ansible_report.json')

        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_mine(self):
        result = os.system('radon-miner extract-metrics {0} {1} ansible all release {2}'.format(self.path_to_repo,
                                                                                                self.path_to_report,
                                                                                                self.path_to_tmp_dir))
        assert result == 0
        assert 'metrics.csv' in os.listdir(self.path_to_tmp_dir)


if __name__ == '__main__':
    unittest.main()
