import unittest

from repominer.mining.base import FixingCommitClassifier
from pydriller.repository import Repository


class BaseFixingCommitClassifierTestSuite(unittest.TestCase):

    def test_init__type_error(self):

        with self.assertRaises(TypeError):
            FixingCommitClassifier(commit=None)

    def test_init__sentence(self):

        for commit in Repository(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                 only_in_branch='main',
                                 only_commits=['3de3d8c2bbccf62ef5698cf33ad258aae5316432']).traverse_commits():

            classifier = FixingCommitClassifier(commit)
            self.assertEqual(classifier.sentences, [['Initial', 'commit']])
