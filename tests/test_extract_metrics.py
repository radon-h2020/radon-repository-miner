import json
import os
import unittest
from pydriller.git_repository import GitRepository
from radonminer.file import LabeledFileDecoder
from radonminer.metrics.ansible import AnsibleMetricsExtractor
from radonminer.metrics.tosca import ToscaMetricsExtractor

ROOT = os.path.realpath(__file__).rsplit(os.sep, 2)[0]
PATH_TO_TEST_DATA = os.path.join(ROOT, 'test_data')
PATH_TO_ANSIBLE_REPO = os.path.join(ROOT, 'test_data', 'adriagalin/ansible.motd')
PATH_TO_TOSCA_REPO = os.path.join(ROOT, 'test_data', 'COLARepo')


class ExtractMetricsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.git_repo = GitRepository(PATH_TO_ANSIBLE_REPO)
        cls.ansible_extractor = AnsibleMetricsExtractor(path_to_repo=PATH_TO_ANSIBLE_REPO)
        cls.tosc_extractor = ToscaMetricsExtractor(path_to_repo=PATH_TO_ANSIBLE_REPO)

        with open(os.path.join(PATH_TO_TEST_DATA, 'ansible_report.json')) as f:
            cls.ansible_labeled_files = json.load(f, cls=LabeledFileDecoder)

        with open(os.path.join(PATH_TO_TEST_DATA, 'tosca_report.json')) as f:
            cls.tosca_labeled_files = json.load(f, cls=LabeledFileDecoder)

    @classmethod
    def tearDownClass(cls):
        if cls.git_repo:
            cls.git_repo.reset()

    def test_ansible_extract(self):
        self.ansible_extractor.extract(labeled_files=self.ansible_labeled_files, product=True, process= True, delta=False, at = 'release')

        assert 'filepath' in self.ansible_extractor.dataset.columns
        assert 'commit' in self.ansible_extractor.dataset.columns
        assert 'committed_at' in self.ansible_extractor.dataset.columns
        assert 'failure_prone' in self.ansible_extractor.dataset.columns
        assert self.ansible_extractor.dataset.shape[1] == 66

    """
    def test_tosca_extract(self):
        self.tosca_extractor.extract(self.tosca_labeled_files, product=True, process= True, delta=False, at = 'release')

        assert 'filepath' in self.ansible_extractor.dataset.columns
        assert 'commit' in self.ansible_extractor.dataset.columns
        assert 'committed_at' in self.ansible_extractor.dataset.columns
        assert 'failure_prone' in self.ansible_extractor.dataset.columns
        assert self.ansible_extractor.dataset.shape[1] == 66
    """

if __name__ == '__main__':
    unittest.main()
