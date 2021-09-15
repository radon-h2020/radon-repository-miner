import os
import unittest
import shutil

from repominer.metrics.ansible import AnsibleMetricsExtractor


class BaseMetricsExtractorTestSuite(unittest.TestCase):
    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

        cls.me = AnsibleMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                         clone_repo_to=cls.path_to_tmp_dir,
                                         at='release')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_get_product_metrics(self):
        content = '---\n- name: Copy WAR file to host\n\tcopy:\n\t\tsrc: helloworld.war\n\t\tdest: /tmp\n'.expandtabs(2)
        self.assertEqual(self.me.get_product_metrics(script=content).keys(), {
            'lines_code',
            'lines_blank',
            'num_conditions',
            'num_keys',
            'num_tokens',
            'text_entropy',
            'avg_play_size',
            'num_distinct_modules',
            'num_parameters',
            'num_tasks',
            'num_unique_names'
        })

    def test_get_product_metrics_type_error(self):
        content = '---\n- name: Copy WAR file to host (invalid)\n\tcopy:\n\t\tsrc: helloworld.war\n\t\tdest: /tmp\n'
        self.assertEqual(len(self.me.get_product_metrics(script=content)), 0)

    def test_ignore_file(self):
        self.assertFalse(self.me.ignore_file(path_to_file='tasks/task1.yml'))
        self.assertTrue(self.me.ignore_file(path_to_file='others/useless.py'))

    def test_extract_at_commit(self):

        self.me.extract([], product=False, process=False, delta=False)
        self.assertEqual(self.me.dataset.shape, (0, 0))


if __name__ == '__main__':
    unittest.main()
