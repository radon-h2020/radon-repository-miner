# !/usr/bin/python
# coding=utf-8

import os
import shutil
import unittest

from argparse import Namespace
from repominer.cli import MinerCLI


class CLIMineFailureProneFilesTestCase(unittest.TestCase):

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
        args = Namespace(info_to_mine='failure-prone-files',
                         host='github',
                         repository='adriagalin/ansible.motd',
                         language='ansible',
                         dest=self.path_to_tmp_dir,
                         verbose=False)

        try:
            MinerCLI(args).mine()
        except SystemExit as exc:
            assert exc.code == 0
            assert 'fixing-commits.json' in os.listdir(self.path_to_tmp_dir)
            assert 'fixed-files.json' in os.listdir(self.path_to_tmp_dir)
            assert 'failure-prone-files.json' in os.listdir(self.path_to_tmp_dir)


if __name__ == '__main__':
    unittest.main()
