import os
import shutil
import unittest

from repominer.mining.base import BaseMiner
from repominer.files import FixedFile


class TestBaseMiner(unittest.TestCase):
    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_init_wrong_url(self):
        with self.assertRaises(ValueError):
            BaseMiner(
                url_to_repo='https://git.com/stefanodallapalma/radon-repository-miner-testing',
                clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
            )

    def test_init_wrong_clone_to(self):
        with self.assertRaises(FileNotFoundError):
            BaseMiner(
                url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
                clone_repo_to=os.path.join('invalid/folder')
            )

    def test_init_commit_hashes(self):
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp'),
            branch='origin/test-base-miner-commits'
        )

        self.assertEqual(miner.commit_hashes, ['3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # Initial commit
                                               'bf4e8b3b47a594a40a10183f7f5f013a248bc4f9',  # Jun 1st 13:54
                                               '730d5fcb9bcba1b6b8d7d14ab9dff45031f194e5'])  # Jun 1st 13:55

    def test_sort_commits(self):
        commits = ['730d5fcb9bcba1b6b8d7d14ab9dff45031f194e5',
                   '3de3d8c2bbccf62ef5698cf33ad258aae5316432',
                   'bf4e8b3b47a594a40a10183f7f5f013a248bc4f9']

        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp'),
            branch='origin/test-base-miner-commits'
        )

        miner.sort_commits(commits)

        self.assertEqual(
            commits, [
                '3de3d8c2bbccf62ef5698cf33ad258aae5316432',
                'bf4e8b3b47a594a40a10183f7f5f013a248bc4f9',
                '730d5fcb9bcba1b6b8d7d14ab9dff45031f194e5'
            ]
        )

    def test_discard_undesired_fixing_commits(self):
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        self.assertIsNone(miner.discard_undesired_fixing_commits(commits=[]))

    def test_ignore_file__abstract(self):
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        self.assertFalse(miner.ignore_file(path_to_file=''))

    def test_get_fixed_files_empty(self):
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        miner.get_fixed_files()
        self.assertListEqual([], miner.fixed_files)

    def test_get_fixing_commits__continue(self):
        """To test if branch in condition:
            if commit.hash in self.fixing_commits:
                continue
        """
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        commits = [
            '3de3d8c2bbccf62ef5698cf33ad258aae5316432',
            'fa91aedc17a7dfb08a60f189c86a9d86dac72b41',
            'ea49aab402a7cb64e9382e764f202d9e6c8f4cbe',
            'c029d7520456e5468d66b56fe176146680520b20',
            'd39fdb44e98869835fe59a86d20d05a9e82d5282',
        ]

        miner.fixing_commits = commits
        miner.get_fixing_commits()
        self.assertListEqual(miner.fixing_commits, commits)

    def test_get_fixed_files_with_one_commit(self):
        """To test if branch in condition: if len(self.fixing_commits) == 1"""
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        miner.fixing_commits = ['3de3d8c2bbccf62ef5698cf33ad258aae5316432']
        miner.get_fixed_files()
        self.assertListEqual([], miner.fixed_files)

    def test_get_fixed_files_with_more_than_one_commits(self):
        """To test else branch in condition: if len(self.fixing_commits) == 1"""
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        miner.fixing_commits = ['3de3d8c2bbccf62ef5698cf33ad258aae5316432', 'c029d7520456e5468d66b56fe176146680520b20']
        miner.get_fixed_files()
        self.assertListEqual([], miner.fixed_files)

    def test_label__return(self):
        """To test the condition:
            if not (self.fixing_commits or self.fixed_files):
                return
        """
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
        )

        miner.fixing_commits = ['3de3d8c2bbccf62ef5698cf33ad258aae5316432']
        miner.fixed_files = []
        for item in miner.label():
            self.assertIsNone(item)

        miner.fixing_commits = []
        miner.fixed_files = [FixedFile(filepath='filepath', fic='', bic='')]
        for item in miner.label():
            self.assertIsNone(item)


if __name__ == '__main__':
    unittest.main()
