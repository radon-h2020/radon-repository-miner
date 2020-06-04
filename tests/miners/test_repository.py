import os
import unittest

from dotenv import load_dotenv

from pydriller import GitRepository
from iacminer.entities.file import LabeledFile
from iacminer.miners.repository import RepositoryMiner

ROOT = os.path.realpath(__file__).rsplit(os.sep, 3)[0]
PATH_TO_REPO = ROOT + '/test_data/adriagalin/ansible.motd'

BUG_RELATED_LABELS = {'bug', 'Bug', 'bug :bug:', 'ansible_bug', 'Type: Bug', 'Type: bug', 'type: bug 🐛', 'type:bug',
                      'type: bug', 'kind/bug', 'kind/bugs', 'bugfix', 'critical-bug', '01 type: bug', 'bug_report',
                      'minor-bug'}

class RepositoryMinerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.git_repo = GitRepository(PATH_TO_REPO)
        cls.git_repo.reset()
        cls.git_repo.checkout('3a8d9b7ed430a3367d8d8616e0ba5d2bddb07b9e')
        cls.repo_miner = RepositoryMiner(os.getenv('GITHUB_ACCESS_TOKEN'), PATH_TO_REPO)

    @classmethod
    def tearDownClass(cls):
        cls.git_repo.reset()

    def test_get_labels(self):
        labels = self.repo_miner.get_labels()
        labels = BUG_RELATED_LABELS.intersection(labels)

        assert labels
        assert len(labels) == 1
        assert labels == {'bug'}

    def test_get_closed_issues(self):
        issues = self.repo_miner.get_closed_issues('bug')
        assert issues is not None
        assert len(issues) == 0

    def test_get_issue_labels(self):
        labels = self.repo_miner.get_issue_labels(3)
        assert not labels

    def test_get_fixing_commits_from_closed_issues(self):
        hashes = self.repo_miner.get_fixing_commits_from_closed_issues()
        assert not hashes

    def test_get_fixing_commits_from_commit_messages(self):
        hashes = self.repo_miner.get_fixing_commits_from_commit_messages()
        assert hashes == {'9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8', 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                          '72377bb59a484ac7c6c6954ce6bf796eb6143f86', 'be34c67e75c2788742f3e87313a0b646af1006db'}

    def test_set_fixing_commits(self):
        self.repo_miner.set_fixing_commits()
        hashes = self.repo_miner.fixing_commits
        assert hashes == {'9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8', 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                          '72377bb59a484ac7c6c6954ce6bf796eb6143f86', 'be34c67e75c2788742f3e87313a0b646af1006db'}

    def test_get_fixing_files(self):
        self.repo_miner.set_fixing_commits()
        fixing_files = self.repo_miner.get_fixing_files()

        assert fixing_files
        assert len(fixing_files) == 3

        assert fixing_files[0].filepath == 'meta/main.yml'
        assert fixing_files[0].fic == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'
        assert fixing_files[0].bics == {'e3a4420937cd9061a6525d541d525ac2167d7322'}

        assert fixing_files[1].filepath == 'tasks/main.yml'
        assert fixing_files[1].fic == 'be34c67e75c2788742f3e87313a0b646af1006db'
        assert fixing_files[1].bics == {'033cd106f8c3f552d98438bf06cb38e7b8f4fbfd',
                                        '9864d99fb99a7444ae1a077909143b5633b0f470'}

        assert fixing_files[2].filepath == 'meta/main.yml'
        assert fixing_files[2].fic == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'
        assert fixing_files[2].bics == {'033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'}

    def test_label(self):

        self.repo_miner.set_fixing_commits()
        labeled_files = self.repo_miner.label(self.repo_miner.get_fixing_files())

        assert labeled_files
        assert len(labeled_files) == 37

        # First meta/main
        assert labeled_files[0].filepath == 'meta/main.yml'
        assert labeled_files[0].commit == '84c7e12d2510db7e0ee20cc343c0e1676de41bc2'
        assert labeled_files[0].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[0].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[1].filepath == 'meta/main.yml'
        assert labeled_files[1].commit == '4e5c8866ae7ce49fdb07d9f0306a7467cec175fb'
        assert labeled_files[1].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[1].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[2].filepath == 'meta/main.yml'
        assert labeled_files[2].commit == 'be34c67e75c2788742f3e87313a0b646af1006db'
        assert labeled_files[2].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[2].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[3].filepath == 'meta/main.yml'
        assert labeled_files[3].commit == '5a23742e4f2cc3cc579773b96dfc29ffcd7f6ab4'
        assert labeled_files[3].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[3].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        # First tasks/main
        assert labeled_files[4].filepath == 'tasks/main.yml'
        assert labeled_files[4].commit == '5a23742e4f2cc3cc579773b96dfc29ffcd7f6ab4'
        assert labeled_files[4].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[4].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert labeled_files[5].filepath == 'meta/main.yml'
        assert labeled_files[5].commit == '9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8'
        assert labeled_files[5].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[5].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[6].filepath == 'tasks/main.yml'
        assert labeled_files[6].commit == '9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8'
        assert labeled_files[6].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[6].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert labeled_files[7].filepath == 'meta/main.yml'
        assert labeled_files[7].commit == '81dfa955dfa0dfe3e72a0c77a057be256894c6a1'
        assert labeled_files[7].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[7].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[8].filepath == 'tasks/main.yml'
        assert labeled_files[8].commit == '81dfa955dfa0dfe3e72a0c77a057be256894c6a1'
        assert labeled_files[8].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[8].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert labeled_files[9].filepath == 'meta/main.yml'
        assert labeled_files[9].commit == '0253259a2e0c39202d56e2f45f19d6878de07404'
        assert labeled_files[9].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[9].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[10].filepath == 'tasks/main.yml'
        assert labeled_files[10].commit == '0253259a2e0c39202d56e2f45f19d6878de07404'
        assert labeled_files[10].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[10].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Last meta/main
        assert labeled_files[11].filepath == 'meta/main.yml'
        assert labeled_files[11].commit == 'e3a4420937cd9061a6525d541d525ac2167d7322'
        assert labeled_files[11].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[11].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert labeled_files[12].filepath == 'tasks/main.yml'
        assert labeled_files[12].commit == 'e3a4420937cd9061a6525d541d525ac2167d7322'
        assert labeled_files[12].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[12].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # ...

        assert labeled_files[32].filepath == 'tasks/main.yml'
        assert labeled_files[32].commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'
        assert labeled_files[32].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[32].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert labeled_files[33].filepath == 'tasks/main.yml'
        assert labeled_files[33].commit == 'be90e54c969797b7d92594a92126df9bd8f8683a'
        assert labeled_files[33].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[33].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Firt meta/main
        assert labeled_files[34].filepath == 'meta/main.yml'
        assert labeled_files[34].commit == 'be90e54c969797b7d92594a92126df9bd8f8683a'
        assert labeled_files[34].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[34].fixing_commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'

        # Last tasks/main
        assert labeled_files[35].filepath == 'tasks/main.yml'
        assert labeled_files[35].commit == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'
        assert labeled_files[35].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[35].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Last meta/main
        assert labeled_files[36].filepath == 'meta/main.yml'
        assert labeled_files[36].commit == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'
        assert labeled_files[36].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[36].fixing_commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'


if __name__ == '__main__':
    unittest.main()
