# !/usr/bin/python
# coding=utf-8

import os
import shutil
import unittest

from repominer.files import FixedFile
from repominer.mining.ansible import AnsibleMiner


class AnsibleMinerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)
        os.environ["TMP_REPOSITORIES_DIR"] = cls.path_to_tmp_dir

        cls.repo_miner = AnsibleMiner(url_to_repo='https://github.com/adriagalin/ansible.motd.git',
                                      branch='master')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)
        del os.environ["TMP_REPOSITORIES_DIR"]

    def setUp(self) -> None:
        self.repo_miner.fixing_commits = list()
        self.repo_miner.exclude_commits = {'e283a1f673b1bd583f2a40645671179e46c9048f',
                                           'fd15570a031fa042ae11e0bb0831e86e1acb6843',
                                           '8a062eea882ba9d7f93634c8f0ac09b821963ad3',
                                           '86c9a39a318240f51961b956e20c1261031966dd'}
        self.repo_miner.exclude_fixed_files = list()

    def test_get_fixing_commits_from_closed_issues(self):
        hashes = self.repo_miner.get_fixing_commits_from_closed_issues(labels={'bug'})
        assert not hashes

    def test_get_fixing_commits_from_commit_messages(self):
        hashes = self.repo_miner.get_fixing_commits_from_commit_messages(regex=r'(bug|fix|error|crash|problem|fail'
                                                                               r'|defect|patch)')
        assert self.repo_miner.fixing_commits == ['72377bb59a484ac7c6c6954ce6bf796eb6143f86',
                                                  'be34c67e75c2788742f3e87313a0b646af1006db',
                                                  'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703']

        assert set(hashes) == {'be34c67e75c2788742f3e87313a0b646af1006db',
                               'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                               '72377bb59a484ac7c6c6954ce6bf796eb6143f86'}

    def test_get_fixing_commits_from_commit_messages_with_exclude_commits(self):
        self.repo_miner.exclude_commits.add('f9ac8bbc68dedb742e5825c5cf47bca8e6f71703')

        hashes = self.repo_miner.get_fixing_commits_from_commit_messages(regex=r'(bug|fix|error|crash|problem|fail'
                                                                               r'|defect|patch)')

        assert self.repo_miner.fixing_commits == ['72377bb59a484ac7c6c6954ce6bf796eb6143f86',
                                                  'be34c67e75c2788742f3e87313a0b646af1006db']

        assert set(hashes) == {'be34c67e75c2788742f3e87313a0b646af1006db',
                               '72377bb59a484ac7c6c6954ce6bf796eb6143f86'}

    def test_discard_non_iac_fixing_commits(self):
        fixing_commits = ['9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8',
                          '72377bb59a484ac7c6c6954ce6bf796eb6143f86',
                          'be34c67e75c2788742f3e87313a0b646af1006db',
                          'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703']

        self.repo_miner.discard_undesired_fixing_commits(fixing_commits)

        assert set(fixing_commits) == {'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                                       '72377bb59a484ac7c6c6954ce6bf796eb6143f86',
                                       'be34c67e75c2788742f3e87313a0b646af1006db'}

    def test_get_fixed_files(self):
        self.repo_miner.get_fixing_commits_from_commit_messages(
            regex=r'(bug|fix|error|crash|problem|fail|defect|patch)')
        fixed_files = self.repo_miner.get_fixed_files()

        assert fixed_files
        assert len(fixed_files) == 3

        assert fixed_files[0].filepath == os.path.join('meta', 'main.yml')
        assert fixed_files[0].fic == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'  # Jun 27, 2019
        assert fixed_files[0].bic == 'e3a4420937cd9061a6525d541d525ac2167d7322'  # Aug 26, 2016

        assert fixed_files[1].filepath == os.path.join('tasks', 'main.yml')
        assert fixed_files[1].fic == 'be34c67e75c2788742f3e87313a0b646af1006db'  # Jun 20, 2019
        assert fixed_files[1].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

        assert fixed_files[2].filepath == os.path.join('meta', 'main.yml')
        assert fixed_files[2].fic == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'  # Aug 15, 2015
        assert fixed_files[2].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

    def test_get_fixed_files_with_exclude_commits(self):
        self.repo_miner.exclude_commits.add('f9ac8bbc68dedb742e5825c5cf47bca8e6f71703')

        self.repo_miner.get_fixing_commits_from_commit_messages(
            regex=r'(bug|fix|error|crash|problem|fail|defect|patch)')
        fixed_files = self.repo_miner.get_fixed_files()

        assert fixed_files
        assert len(fixed_files) == 2

        assert fixed_files[0].filepath == os.path.join('tasks', 'main.yml')
        assert fixed_files[0].fic == 'be34c67e75c2788742f3e87313a0b646af1006db'  # Jun 20, 2019
        assert fixed_files[0].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

        assert fixed_files[1].filepath == os.path.join('meta', 'main.yml')
        assert fixed_files[1].fic == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'  # Aug 15, 2015
        assert fixed_files[1].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

    def test_get_fixed_files_with_exclude_files(self):
        self.repo_miner.exclude_fixed_files = [
            FixedFile(filepath=os.path.join('meta', 'main.yml'),
                      fic='f9ac8bbc68dedb742e5825c5cf47bca8e6f71703',
                      bic='e3a4420937cd9061a6525d541d525ac2167d7322')
        ]

        self.repo_miner.get_fixing_commits_from_commit_messages(r'(bug|fix|error|crash|problem|fail|defect|patch)')
        fixed_files = self.repo_miner.get_fixed_files()

        assert fixed_files
        assert len(fixed_files) == 2

        assert fixed_files[0].filepath == os.path.join('tasks', 'main.yml')
        assert fixed_files[0].fic == 'be34c67e75c2788742f3e87313a0b646af1006db'  # Jun 20, 2019
        assert fixed_files[0].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

        assert fixed_files[1].filepath == os.path.join('meta', 'main.yml')
        assert fixed_files[1].fic == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'  # Aug 15, 2015
        assert fixed_files[1].bic == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'  # Aug 13, 2015

    def test_mining_pipeline(self):
        self.repo_miner.fixing_commits = list()  # reset list of fixing-commits
        self.repo_miner.get_fixing_commits_from_commit_messages(
            regex=r'(bug|fix|error|crash|problem|fail|defect|patch)')
        self.repo_miner.get_fixed_files()
        failure_prone_files = [failure_prone_file for failure_prone_file in self.repo_miner.label()]

        assert failure_prone_files
        assert len(failure_prone_files) == 37

        # First meta/main
        assert failure_prone_files[0].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[0].commit == '84c7e12d2510db7e0ee20cc343c0e1676de41bc2'
        assert failure_prone_files[0].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[1].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[1].commit == '4e5c8866ae7ce49fdb07d9f0306a7467cec175fb'
        assert failure_prone_files[1].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[2].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[2].commit == 'be34c67e75c2788742f3e87313a0b646af1006db'
        assert failure_prone_files[2].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[3].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[3].commit == '5a23742e4f2cc3cc579773b96dfc29ffcd7f6ab4'
        assert failure_prone_files[3].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        # First tasks/main
        assert failure_prone_files[4].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[4].commit == '5a23742e4f2cc3cc579773b96dfc29ffcd7f6ab4'
        assert failure_prone_files[4].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert failure_prone_files[5].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[5].commit == '9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8'
        assert failure_prone_files[5].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[6].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[6].commit == '9cf96c3670b65b825d3ebc2575b0aa300f3e7bf8'
        assert failure_prone_files[6].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert failure_prone_files[7].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[7].commit == '81dfa955dfa0dfe3e72a0c77a057be256894c6a1'
        assert failure_prone_files[7].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[8].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[8].commit == '81dfa955dfa0dfe3e72a0c77a057be256894c6a1'
        assert failure_prone_files[8].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert failure_prone_files[9].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[9].commit == '0253259a2e0c39202d56e2f45f19d6878de07404'
        assert failure_prone_files[9].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[10].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[10].commit == '0253259a2e0c39202d56e2f45f19d6878de07404'
        assert failure_prone_files[10].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Last meta/main
        assert failure_prone_files[11].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[11].commit == 'e3a4420937cd9061a6525d541d525ac2167d7322'
        assert failure_prone_files[11].fixing_commit == 'f9ac8bbc68dedb742e5825c5cf47bca8e6f71703'

        assert failure_prone_files[12].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[12].commit == 'e3a4420937cd9061a6525d541d525ac2167d7322'
        assert failure_prone_files[12].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # ...

        assert failure_prone_files[31].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[31].commit == 'b0e8f1f7c7f4412d8f389cbd68d52b0090be8620'
        assert failure_prone_files[31].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        assert failure_prone_files[32].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[32].commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'
        assert failure_prone_files[32].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # First meta/main
        assert failure_prone_files[33].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[33].commit == 'be90e54c969797b7d92594a92126df9bd8f8683a'
        assert failure_prone_files[33].fixing_commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'

        assert failure_prone_files[34].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[34].commit == 'be90e54c969797b7d92594a92126df9bd8f8683a'
        assert failure_prone_files[34].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'

        # Last meta/main
        assert failure_prone_files[35].filepath == os.path.join('meta', 'main.yml')
        assert failure_prone_files[35].commit == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'
        assert failure_prone_files[35].fixing_commit == '72377bb59a484ac7c6c6954ce6bf796eb6143f86'

        # Last tasks/main
        assert failure_prone_files[36].filepath == os.path.join('tasks', 'main.yml')
        assert failure_prone_files[36].commit == '033cd106f8c3f552d98438bf06cb38e7b8f4fbfd'
        assert failure_prone_files[36].fixing_commit == 'be34c67e75c2788742f3e87313a0b646af1006db'


if __name__ == '__main__':
    unittest.main()
