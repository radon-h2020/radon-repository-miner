import os
import shutil
import unittest

from repominer.mining.base import BaseMiner

class BaseMinerInit(unittest.TestCase):

    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_wrong_url(self):
        with self.assertRaises(ValueError):
            BaseMiner(
                url_to_repo='https://git.com/stefanodallapalma/radon-repository-miner-testing',
                clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp')
            )

    def test_wrong_clone_to(self):
        with self.assertRaises(FileNotFoundError):
            BaseMiner(
                url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
                clone_repo_to=os.path.join('invalid/folder')
            )

    def test_commit_hashes(self):
        miner = BaseMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp'),
            branch='origin/test-base-miner-commits'
        )

        self.assertEqual(miner.commit_hashes, ['3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # Initial commit
                                               'bf4e8b3b47a594a40a10183f7f5f013a248bc4f9',  # Jun 1st 13:54
                                               '730d5fcb9bcba1b6b8d7d14ab9dff45031f194e5'])  # Jun 1st 13:55


if __name__ == '__main__':
    unittest.main()
