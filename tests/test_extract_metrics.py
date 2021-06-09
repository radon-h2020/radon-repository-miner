import json
import os
import shutil
import unittest

from repominer.files import FailureProneFileDecoder
from repominer.metrics.ansible import AnsibleMetricsExtractor
from repominer.metrics.tosca import ToscaMetricsExtractor

ROOT = os.path.realpath(__file__).rsplit(os.sep, 2)[0]
PATH_TO_TEST_DATA = os.path.join(ROOT, 'test_data')


class ExtractMetricsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

        path_to_ansible_repo = os.path.join(os.getcwd(), 'test_data', 'repositories', 'ansible.motd')
        path_to_tosca_repo = os.path.join(os.getcwd(), 'test_data', 'repositories', 'COLARepo')
        path_to_remote_ansible_repo = 'https://github.com/adriagalin/ansible.motd.git'

        cls.ansible_extractor = AnsibleMetricsExtractor(path_to_repo=path_to_ansible_repo,
                                                        at='release',
                                                        clone_repo_to=cls.path_to_tmp_dir)

        cls.tosca_extractor = ToscaMetricsExtractor(path_to_repo=path_to_tosca_repo,
                                                    at='release',
                                                    clone_repo_to=cls.path_to_tmp_dir)

        cls.remote_ansible_extractor = AnsibleMetricsExtractor(path_to_repo=path_to_remote_ansible_repo,
                                                               at='release',
                                                               clone_repo_to=cls.path_to_tmp_dir)

        with open(os.path.join(PATH_TO_TEST_DATA, 'ansible_report.json')) as f:
            cls.ansible_labeled_files = json.load(f, cls=FailureProneFileDecoder)

        with open(os.path.join(PATH_TO_TEST_DATA, 'tosca_report.json')) as f:
            cls.tosca_labeled_files = json.load(f, cls=FailureProneFileDecoder)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_ansible_extract(self):
        self.ansible_extractor.extract(labeled_files=self.ansible_labeled_files,
                                       product=True,
                                       process=True,
                                       delta=False)

        assert 'filepath' in self.ansible_extractor.dataset.columns
        assert 'commit' in self.ansible_extractor.dataset.columns
        assert 'committed_at' in self.ansible_extractor.dataset.columns
        assert 'failure_prone' in self.ansible_extractor.dataset.columns
        assert self.ansible_extractor.dataset.shape[1] == 66
        assert self.ansible_extractor.dataset.failure_prone.to_list().count(0) > 0
        assert self.ansible_extractor.dataset.failure_prone.to_list().count(1) > 1

#     def test_tosca_extract(self):
#         self.tosca_extractor.extract(self.tosca_labeled_files, product=True, process=True, delta=False)

#         assert 'filepath' in self.tosca_extractor.dataset.columns
#         assert 'commit' in self.tosca_extractor.dataset.columns
#         assert 'committed_at' in self.tosca_extractor.dataset.columns
#         assert 'failure_prone' in self.tosca_extractor.dataset.columns
#         assert self.tosca_extractor.dataset.shape[1] == 27

    def test_remote_ansible_extract(self):
        self.remote_ansible_extractor.extract(labeled_files=self.ansible_labeled_files,
                                              product=True,
                                              process=True,
                                              delta=False)

        assert 'filepath' in self.ansible_extractor.dataset.columns
        assert 'commit' in self.ansible_extractor.dataset.columns
        assert 'committed_at' in self.ansible_extractor.dataset.columns
        assert 'failure_prone' in self.ansible_extractor.dataset.columns
        assert self.ansible_extractor.dataset.shape[1] == 66
        assert self.ansible_extractor.dataset.failure_prone.to_list().count(0) > 0
        assert self.ansible_extractor.dataset.failure_prone.to_list().count(1) > 1


if __name__ == '__main__':
    unittest.main()
