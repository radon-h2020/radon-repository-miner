import git
import os
import pytest
import shutil

from datetime import datetime
import iacminer.mygit as mygit
from iacminer.entities.file import LabeledFile
from iacminer.miners.repository_miner import RepositoryMiner
from iacminer.miners.labeling import LabelTechnique

from dotenv import load_dotenv
load_dotenv()


BUG_RELATED_LABELS = set(['bug', 'Bug', 'bug :bug:', 'ansible_bug', 'Type: Bug', 'Type: bug',
                          'type: bug 🐛', 'type:bug', 'type: bug', 'kind/bug', 'kind/bugs',
                          'bugfix', 'critical-bug', '01 type: bug', 'bug_report', 'minor-bug'])

class TestClass():

    def setup_class(self):
        # Clone    
        path_to_owner = os.path.join('tests', 'tmp', 'cloudalchemy')
        if not os.path.isdir(path_to_owner):
            os.makedirs(path_to_owner)

        print(f'\nCloning into {path_to_owner}')

        git.Git(path_to_owner).clone(f'https://github.com/cloudalchemy/ansible-node-exporter.git')
        # TODO checkout to a specific commit to avoid new data make fail tests

    def teardown_class(self):
        # Delete cloned repo
        path_to_owner = os.path.join('tests', 'tmp', 'cloudalchemy')
        if os.path.isdir(path_to_owner):
            shutil.rmtree(path_to_owner)

    def setup_method(self):
        pass

    def teardown_method(self):
        pass


    def test_get_labels(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        labels = g.get_labels('cloudalchemy/ansible-node-exporter')
        
        # Keep only the labels related to a bug
        labels = BUG_RELATED_LABELS.intersection(labels)
        
        assert labels
        assert len(labels) == 1
        assert labels == {'bug'}

    def test_get_closed_issues(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        issues = g.get_closed_issues('cloudalchemy/ansible-node-exporter', 'bug')
        
        assert issues
        assert len(issues) == 5

    def test_set_fixing_commits(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'cloudalchemy', 'ansible-node-exporter')
        )

        miner.set_fixing_commits()
        fixing_commits = miner.fixing_commits
        assert fixing_commits
        assert len(fixing_commits) == 1 
        assert fixing_commits == {'2477fe81d0a4485e34eac332ac4e064a742e01b5'}

    def test_get_fixing_files(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'cloudalchemy', 'ansible-node-exporter')
        )

        miner.set_fixing_commits()
        fixing_files = miner.get_fixing_files()
        assert fixing_files
        assert len(fixing_files) == 1
        assert fixing_files[0].filepath == 'tasks/install.yml'
        assert fixing_files[0].fix_commit == '2477fe81d0a4485e34eac332ac4e064a742e01b5'
        assert fixing_files[0].bics == {'212db9feaf274b349af10d7edfaaa377eb94c272'}

    def test_label_file(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'cloudalchemy', 'ansible-node-exporter')
        )

        labeled_files = miner.mine(LabelTechnique.DEFECTIVE_FROM_OLDEST_BIC)
        
        assert labeled_files
        assert len(labeled_files) == 88

        labeled_files[0].filepath = 'tasks/install.yml'
        labeled_files[0].commit = '3f852639ecece4b9d1df3b09c1d79fa277d202fe'
        labeled_files[0].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[0].ref = 'tasks/install.yml'

        labeled_files[86].filepath = 'tasks/install.yml'
        labeled_files[86].commit = '5854ae268658788e1b791458bff68962f8d8c84e'    # Commit after the oldest bic for the file tasks/install.yml
        labeled_files[86].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[86].ref = 'tasks/install.yml'

        labeled_files[87].filepath = 'tasks/install.yml'
        labeled_files[87].commit = '212db9feaf274b349af10d7edfaaa377eb94c272'    # Oldest bic for the file tasks/install.yml
        labeled_files[87].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[87].ref = 'tasks/install.yml'