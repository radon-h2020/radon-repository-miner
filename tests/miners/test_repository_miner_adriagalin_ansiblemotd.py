import git
import os
import pytest
import shutil

from datetime import datetime
import iacminer.mygit as mygit
from iacminer.entities.file import LabeledFile
from iacminer.miners.repository import RepositoryMiner
from iacminer.miners.labeling import LabelingTechnique

from dotenv import load_dotenv
load_dotenv()


BUG_RELATED_LABELS = set(['bug', 'Bug', 'bug :bug:', 'ansible_bug', 'Type: Bug', 'Type: bug',
                          'type: bug 🐛', 'type:bug', 'type: bug', 'kind/bug', 'kind/bugs',
                          'bugfix', 'critical-bug', '01 type: bug', 'bug_report', 'minor-bug'])

class TestClass():

    def setup_class(self):
        # Clone    
        path_to_owner = os.path.join('tests', 'tmp', 'adriagalin')
        if not os.path.isdir(path_to_owner):
            os.makedirs(path_to_owner)

        print(f'\nCloning into {path_to_owner}')

        git.Git(path_to_owner).clone(f'https://github.com/adriagalin/ansible.motd.git')
        # TODO checkout to a specific commit to avoid new data make fail tests

    def teardown_class(self):
        # Delete cloned repo
        path_to_owner = os.path.join('tests', 'tmp', 'adriagalin')
        if os.path.isdir(path_to_owner):
            shutil.rmtree(path_to_owner)

    def setup_method(self):
        pass

    def teardown_method(self):
        pass


    def test_get_labels(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        labels = g.get_labels('adriagalin/ansible.motd')
        
        # Keep only the labels related to a bug
        labels = BUG_RELATED_LABELS.intersection(labels)
        
        assert labels
        assert len(labels) == 1
        assert labels == {'bug'}

    def test_get_closed_issues(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        issues = g.get_closed_issues('adriagalin/ansible.motd', 'bug')
        
        assert issues is not None
        assert len(issues) == 0

    def test_set_fixing_commits(self):
        """
        Test mine() using LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC
        """

        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'adriagalin', 'ansible.motd')
        )

        miner.set_fixing_commits()
        fixing_commits = miner.fixing_commits
        assert fixing_commits
        assert len(fixing_commits) == 2
        assert fixing_commits == {'be34c67e75c2788742f3e87313a0b646af1006db', 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'}

    def test_get_fixing_files(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'adriagalin', 'ansible.motd')
        )

        miner.set_fixing_commits()
        fixing_files = miner.get_fixing_files()
        
        assert fixing_files
        assert len(fixing_files) == 2

        assert fixing_files[0].filepath == 'meta/main.yml'
        assert fixing_files[0].fic == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'
        assert fixing_files[0].bics == {'e3a4420937cd9061a6525d541d525ac2167d7322'}
        
        assert fixing_files[1].filepath == 'tasks/main.yml'
        assert fixing_files[1].fic == 'be34c67e75c2788742f3e87313a0b646af1006db'
        assert fixing_files[1].bics == {'033cd106f8c3f552d98438bf06cb38e7b8f4fbfd', '9864d99fb99a7444ae1a077909143b5633b0f470'}

    def test_label_at_release(self):
        """
        Test mine() with LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC
        """

        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'adriagalin', 'ansible.motd')
        )

        labeled_files = miner.mine(LabelingTechnique.DEFECTIVE_FROM_OLDEST_BIC)
        
        assert labeled_files
        assert len(labeled_files) == 35

        # First meta/main 
        assert labeled_files[0].filepath == 'meta/main.yml'
        assert labeled_files[0].commit == '84c7e12d2510db7e0ee20cc343c0e1676de41bc2'
        assert labeled_files[0].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[0].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        # First tasks/main 
        assert labeled_files[4].filepath == 'tasks/main.yml'
        assert labeled_files[4].commit == '5a23742e4f2cc3cc579773b96dfc29ffcd7f6ab4'
        assert labeled_files[4].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[4].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Last meta/main
        assert labeled_files[11].filepath == 'meta/main.yml'
        assert labeled_files[11].commit == 'e3a4420937cd9061a6525d541d525ac2167d7322'
        assert labeled_files[11].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[11].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        # Last tasks/main
        assert labeled_files[34].filepath == 'tasks/main.yml'
        assert labeled_files[34].commit == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'
        assert labeled_files[34].label == LabeledFile.Label.DEFECT_PRONE
        assert labeled_files[34].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'