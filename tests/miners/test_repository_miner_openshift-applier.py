import git
import os
import pytest
import shutil

from datetime import datetime
import iacminer.mygit as mygit
from iacminer.entities.file import LabeledFile
from iacminer.miners.repository_miner import RepositoryMiner

from dotenv import load_dotenv
load_dotenv()


BUG_RELATED_LABELS = set(['bug', 'Bug', 'bug :bug:', 'ansible_bug', 'Type: Bug', 'Type: bug',
                          'type: bug 🐛', 'type:bug', 'type: bug', 'kind/bug', 'kind/bugs',
                          'bugfix', 'critical-bug', '01 type: bug', 'bug_report', 'minor-bug'])

class TestClass():

    def setup_class(self):
        # Clone    
        path_to_owner = os.path.join('tests', 'tmp', 'redhat-cop')
        if not os.path.isdir(path_to_owner):
            os.makedirs(path_to_owner)

        print(f'\nCloning into {path_to_owner}')

        git.Git(path_to_owner).clone(f'https://github.com/redhat-cop/openshift-applier.git')
        # TODO checkout at 944f536233479004ee5919be0592fa3ba295bfd8 to avoid new data make fail tests

    def teardown_class(self):
        # Delete cloned repo
        path_to_owner = os.path.join('tests', 'tmp', 'redhat-cop')
        if os.path.isdir(path_to_owner):
            shutil.rmtree(path_to_owner)

    def test_get_labels(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        labels = g.get_labels('redhat-cop/openshift-applier')
        
        # Keep only the labels related to a bug
        labels = BUG_RELATED_LABELS.intersection(labels)
        
        assert labels
        assert len(labels) == 1
        assert labels == {'bug'}

    def test_get_closed_issues(self):
        g = mygit.Git(os.getenv('GITHUB_ACCESS_TOKEN'))
        issues = g.get_closed_issues('redhat-cop/openshift-applier', 'bug')
        assert issues
        assert len(issues) == 7

    def test_set_fixing_commits(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'redhat-cop', 'openshift-applier')
        )

        miner.set_fixing_commits()
        fixing_commits = miner.fixing_commits
        assert fixing_commits
        assert len(fixing_commits) == 2 
        assert fixing_commits == {'3dae9cd54e7f8b1706a8de5f91338ded600a4127', 'f375d862c35ef1d28683a9979b32000917b12648'}


    def test_get_fixing_files(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'redhat-cop', 'openshift-applier')
        )

        miner.set_fixing_commits()
        fixing_files = miner.get_fixing_files()
        assert fixing_files
        assert len(fixing_files) == 3

        assert fixing_files[0].filepath == 'roles/openshift-applier/tasks/process-template.yml'
        assert fixing_files[0].fix_commit == 'f375d862c35ef1d28683a9979b32000917b12648'
        assert fixing_files[0].bic_commit == '0b43e79a8421477e3e25e8c96569f567179e22dc'

        assert fixing_files[1].filepath == 'roles/openshift-applier/tasks/process-file.yml'
        assert fixing_files[1].fix_commit == '3dae9cd54e7f8b1706a8de5f91338ded600a4127'
        assert fixing_files[1].bic_commit == '0b43e79a8421477e3e25e8c96569f567179e22dc'

        assert fixing_files[2].filepath == 'roles/openshift-applier/tasks/process-one-entry.yml'
        assert fixing_files[2].fix_commit == '3dae9cd54e7f8b1706a8de5f91338ded600a4127'
        assert fixing_files[2].bic_commit == '0b43e79a8421477e3e25e8c96569f567179e22dc'


    def test_label_file(self):
        miner = RepositoryMiner(
            os.path.join('tests', 'tmp', 'redhat-cop', 'openshift-applier')
        )

        labeled_files = miner.mine()
        
        assert labeled_files
        assert len(labeled_files) == 129

        labeled_files[0].filepath = 'roles/openshift-applier/tasks/process-template.yml'
        labeled_files[0].commit = '50af08857bef4eef144d97a2764feb5cead5f50f'
        labeled_files[0].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[0].ref = 'roles/openshift-applier/tasks/process-template.yml'

        labeled_files[36].filepath = 'roles/openshift-applier/tasks/process-template.yml'
        labeled_files[36].commit = '6f64f1dc0e1474733b13e0ceb06b614102efa50f'
        labeled_files[36].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[36].ref = 'roles/openshift-applier/tasks/process-template.yml'

        labeled_files[37].filepath = 'roles/openshift-applier/tasks/process-template.yml'
        labeled_files[37].commit = '0b43e79a8421477e3e25e8c96569f567179e22dc'
        labeled_files[37].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[37].ref = 'roles/openshift-applier/tasks/process-template.yml'

        labeled_files[38].filepath = 'roles/openshift-applier/tasks/process-template.yml'
        labeled_files[38].commit = '1f0d2add97205cf46be9c7d2dbdbbf79f0408b4e'
        labeled_files[38].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[38].ref = 'roles/openshift-applier/tasks/process-template.yml'

        ###
        labeled_files[39].filepath = 'roles/openshift-applier/tasks/process-file.yml'
        labeled_files[39].commit = '4a288ea72ef42644bfddfc87914a78cba0bac198'
        labeled_files[39].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[39].ref = 'roles/openshift-applier/tasks/process-file.yml'

        labeled_files[43].filepath = 'roles/openshift-applier/tasks/process-file.yml'
        labeled_files[43].commit = '6f64f1dc0e1474733b13e0ceb06b614102efa50f'
        labeled_files[43].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[43].ref = 'roles/openshift-applier/tasks/process-file.yml'

        labeled_files[44].filepath = 'roles/openshift-applier/tasks/process-file.yml'
        labeled_files[44].commit = '0b43e79a8421477e3e25e8c96569f567179e22dc'
        labeled_files[44].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[44].ref = 'roles/openshift-applier/tasks/process-file.yml'

        labeled_files[45].filepath = 'roles/openshift-applier/tasks/process-file.yml'
        labeled_files[45].commit = '1f0d2add97205cf46be9c7d2dbdbbf79f0408b4e'
        labeled_files[45].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[45].ref = 'roles/openshift-applier/tasks/process-file.yml'

        #####
        labeled_files[46].filepath = 'roles/openshift-applier/tasks/process-one-entry.yml'
        labeled_files[46].commit = '4a288ea72ef42644bfddfc87914a78cba0bac198'
        labeled_files[46].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[46].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[51].filepath = 'roles/openshift-applier/tasks/process-one-entry.yml'
        labeled_files[51].commit = '6f64f1dc0e1474733b13e0ceb06b614102efa50f'
        labeled_files[51].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[51].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[52].filepath = 'roles/openshift-applier/tasks/process-one-entry.yml'
        labeled_files[52].commit = '0b43e79a8421477e3e25e8c96569f567179e22dc'
        labeled_files[52].label = LabeledFile.Label.DEFECT_PRONE
        labeled_files[52].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[53].filepath = 'roles/openshift-applier/tasks/process-one-entry.yml'
        labeled_files[53].commit = '1f0d2add97205cf46be9c7d2dbdbbf79f0408b4e'
        labeled_files[53].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[53].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[82].filepath = 'roles/openshift-applier/tasks/process-one-entry.yml'
        labeled_files[82].commit = 'a5470ea1371f7f24770147186dc6a5c1b0dcdddf'
        labeled_files[82].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[82].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[83].filepath = 'tasks/process-one-entry.yml'
        labeled_files[83].commit = '0ce83da4b940616a4ef98263d027ea090c8beaf4'
        labeled_files[83].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[83].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

        labeled_files[128].filepath = 'tasks/process-one-entry.yml'
        labeled_files[128].commit = '31c7db0ac06ff70256553d2ff0e08de5069888c0'
        labeled_files[128].label = LabeledFile.Label.DEFECT_FREE
        labeled_files[128].ref = 'roles/openshift-applier/tasks/process-one-entry.yml'

