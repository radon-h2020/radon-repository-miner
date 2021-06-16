import os
import unittest
import shutil

from repominer.files import FailureProneFile
from repominer.metrics.base import BaseMetricsExtractor, is_remote, get_content


class BaseMetricsExtractorTestSuite(unittest.TestCase):
    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_is_remote(self):
        self.assertTrue(is_remote('https://git.com/stefanodallapalma/radon-repository-miner-testing'))
        self.assertTrue(is_remote('git@github.com:stefanodallapalma/radon-repository-miner-testing.git'))
        self.assertFalse(is_remote(self.path_to_tmp_dir))

    def test_get_content_ok(self):
        path_to_file = os.path.join(self.path_to_tmp_dir, 'tmp_file.py')
        with open(path_to_file, 'w') as f:
            f.write('hooray!')

        content = get_content(path_to_file)
        self.assertEqual(content, 'hooray!')

    def test_get_content_none(self):
        self.assertIsNone(get_content(self.path_to_tmp_dir))

    def test_get_content_none_2(self):
        """ Test return None after having arose UnicodeDecodeError
        """
        path_to_file = os.path.join(self.path_to_tmp_dir, 'tmp_file.py')
        with open(path_to_file, 'wb') as f:
            f.write(b'\x81')

        self.assertIsNone(get_content(path_to_file))

    def test_init_ValueError_1(self):
        with self.assertRaises(ValueError):
            BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                 clone_repo_to=self.path_to_tmp_dir,
                                 at='file')

    def test_init_ValueError_2(self):
        with self.assertRaises(ValueError):
            BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                 clone_repo_to=None,
                                 at='release')

    def test_init_ValueError_3(self):
        with self.assertRaises(ValueError):
            BaseMetricsExtractor(path_to_repo='https://bitbucket.com/stefanodallapalma/radon-repository-miner-testing',
                                 clone_repo_to=self.path_to_tmp_dir,
                                 at='release')

    def test_commits_at_commit(self):
            me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                      clone_repo_to=self.path_to_tmp_dir,
                                      at='commit')

            self.assertEqual(me.commits_at, [
                '3de3d8c2bbccf62ef5698cf33ad258aae5316432',
                'fa91aedc17a7dfb08a60f189c86a9d86dac72b41',
                'ea49aab402a7cb64e9382e764f202d9e6c8f4cbe',
                'c029d7520456e5468d66b56fe176146680520b20',
                'd39fdb44e98869835fe59a86d20d05a9e82d5282',
                '75da5889425815009cc0eb4bdff68f59024d351f',
                'f494eac8c6e7acad5bdc6acf32c6b40b1a11c926'
            ])

    def test_commits_at_release(self):
            me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                      clone_repo_to=self.path_to_tmp_dir,
                                      at='release')

            self.assertEqual(me.commits_at, [
                'd39fdb44e98869835fe59a86d20d05a9e82d5282',
                '75da5889425815009cc0eb4bdff68f59024d351f',
                'f494eac8c6e7acad5bdc6acf32c6b40b1a11c926'
            ])

    def test_get_files(self):
            me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                      clone_repo_to=self.path_to_tmp_dir,
                                      at='release')

            self.assertEqual(me.get_files(), {
                'LICENSE',
                'README.md',
                'test_is_comment_changed-renamed.py'
            })

    def test_get_product_metrics__abstract(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='release')

        self.assertDictEqual(me.get_product_metrics(script=''), {})

    def test_get_process_metrics(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='release')

        metrics = me.get_process_metrics(from_commit='d39fdb44e98869835fe59a86d20d05a9e82d5282',
                                         to_commit='c029d7520456e5468d66b56fe176146680520b20')

        self.assertIn('dict_change_set_max', metrics)
        self.assertIn('dict_change_set_avg', metrics)
        self.assertIn('dict_code_churn_count', metrics)
        self.assertIn('dict_code_churn_max', metrics)
        self.assertIn('dict_code_churn_avg', metrics)
        self.assertIn('dict_commits_count', metrics)
        self.assertIn('dict_contributors_count', metrics)
        self.assertIn('dict_minor_contributors_count', metrics)
        self.assertIn('dict_highest_contributor_experience', metrics)
        self.assertIn('dict_hunks_median', metrics)
        self.assertIn('dict_additions', metrics)
        self.assertIn('dict_additions_max', metrics)
        self.assertIn('dict_additions_avg', metrics)
        self.assertIn('dict_deletions', metrics)
        self.assertIn('dict_deletions_max', metrics)
        self.assertIn('dict_deletions_avg', metrics)

    def test_ignore_file__abstract(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='release')

        self.assertFalse(me.ignore_file(path_to_file='fake/path/to/file.txt'))

    def test_to_csv(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='release')

        me.to_csv(os.path.join(self.path_to_tmp_dir, 'test_to.cvs'))
        self.assertIn('test_to.cvs', os.listdir(self.path_to_tmp_dir))

    def test_extract_at_release(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='release')

        labeled_files = [FailureProneFile(filepath='test_is_comment_changed.py',
                                          commit='c029d7520456e5468d66b56fe176146680520b20',
                                          fixing_commit='d39fdb44e98869835fe59a86d20d05a9e82d5282')]

        me.extract(labeled_files, product=True, process=False, delta=False)
        self.assertEqual(me.dataset.shape, (9, 4))

        me.extract(labeled_files, product=False, process=True, delta=False)
        self.assertEqual(me.dataset.shape, (9, 20))

        me.extract(labeled_files, product=False, process=False, delta=True)
        self.assertEqual(me.dataset.shape, (9, 4))

        me.extract(labeled_files, product=True, process=False, delta=True)
        self.assertEqual(me.dataset.shape, (9, 4))

        me.extract(labeled_files, product=False, process=True, delta=True)
        self.assertEqual(me.dataset.shape, (9, 36))

        labeled_files = [FailureProneFile(filepath='test_is_comment_changed.py',
                                          commit='d39fdb44e98869835fe59a86d20d05a9e82d5282',
                                          fixing_commit='75da5889425815009cc0eb4bdff68f59024d351f')]

        me.extract(labeled_files, product=True, process=False, delta=False)
        self.assertEqual(me.dataset.shape, (9, 4))
        self.assertEqual(me.dataset.failure_prone.to_list().count(0), 8)
        self.assertEqual(me.dataset.failure_prone.to_list().count(1), 1)

    def test_extract_at_commit(self):
        me = BaseMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                  clone_repo_to=self.path_to_tmp_dir,
                                  at='commit')

        me.extract([], product=False, process=False, delta=False)
        self.assertEqual(me.dataset.shape, (18, 4))
        commits = list(me.dataset.commit.unique())
        self.assertIn('3de3d8c2bbccf62ef5698cf33ad258aae5316432', commits)
        self.assertIn('fa91aedc17a7dfb08a60f189c86a9d86dac72b41', commits)
        self.assertIn('ea49aab402a7cb64e9382e764f202d9e6c8f4cbe', commits)
        self.assertIn('c029d7520456e5468d66b56fe176146680520b20', commits)
        self.assertIn('d39fdb44e98869835fe59a86d20d05a9e82d5282', commits)
        self.assertIn('75da5889425815009cc0eb4bdff68f59024d351f', commits)
        self.assertIn('f494eac8c6e7acad5bdc6acf32c6b40b1a11c926', commits)


if __name__ == '__main__':
    unittest.main()
