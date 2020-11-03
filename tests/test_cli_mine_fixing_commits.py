# !/usr/bin/python
# coding=utf-8

import json
import os
import shutil
import unittest


class CLIMineFixingCommitsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)
        os.environ["TMP_REPOSITORIES_DIR"] = cls.path_to_tmp_dir

        # File containing commits to exclude
        cls.exclude_commits_file = os.path.join(cls.path_to_tmp_dir, 'exclude_commits.json')
        with open(cls.exclude_commits_file, 'w') as f:
            json.dump(['e283a1f673b1bd583f2a40645671179e46c9048f',
                       'fd15570a031fa042ae11e0bb0831e86e1acb6843',
                       '8a062eea882ba9d7f93634c8f0ac09b821963ad3',
                       '86c9a39a318240f51961b956e20c1261031966dd',
                       'be34c67e75c2788742f3e87313a0b646af1006db',
                       'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'], f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)
        del os.environ["TMP_REPOSITORIES_DIR"]

    def test_mine_fixing_commits(self):
        result = os.system(
            'repo-miner mine fixing-commits github ansible adriagalin/ansible.motd {}'.format(self.path_to_tmp_dir))
        assert result == 0

        with open(os.path.join(self.path_to_tmp_dir, 'fixing-commits.json'), 'r') as f:
            fixing_commits = json.load(f)
            assert set(fixing_commits) == {'e283a1f673b1bd583f2a40645671179e46c9048f',
                                           'be34c67e75c2788742f3e87313a0b646af1006db',
                                           'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                                           '72377bb59a484ac7c6c6954ce6bf796eb6143f86'}

    def test_mine_fixing_commits_with_exclude(self):
        result = os.system(
            'repo-miner mine fixing-commits github ansible adriagalin/ansible.motd {0} --exclude-commits {1}'.format(self.path_to_tmp_dir,
                                                                                                                     self.exclude_commits_file))
        assert result == 0

        with open(os.path.join(self.path_to_tmp_dir, 'fixing-commits.json'), 'r') as f:
            fixing_commits = json.load(f)
            assert set(fixing_commits) == {'72377bb59a484ac7c6c6954ce6bf796eb6143f86'}


if __name__ == '__main__':
    unittest.main()
