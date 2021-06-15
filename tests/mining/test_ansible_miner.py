import os
import shutil
import unittest

from repominer.mining.ansible import AnsibleMiner
from repominer.files import FixedFile, FailureProneFile


class AnsibleMinerInit(unittest.TestCase):

    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

        cls.miner = AnsibleMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp'),
            branch='origin/test-ansible-miner'
        )

        # cls.miner.get_fixing_commits()
        # cls.miner.get_fixed_files()
        # cls.failure_prone_files = list(file for file in cls.miner.label())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_commit_hashes(self):

        self.assertEqual(
            self.miner.commit_hashes,
            ['3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # Initial commit
             '9cbfa528b26f1d222b1b7954eef41f55d2026f4b',
             '9cae22d8c88d04bd19e51623ed41e8805651aaed',
             'e14240d8ca0ffd3ca8f093f39111d048819ab909',
             '755efda3359954588c8486272b17979b3a6512a2',
             'd07ed2f58c7cbabee89dbc60a62036f22c23394a',
             'e7df3e45e2e27a0dc16806a834b50d0856d350fe',
             '70257245257cd899b6f26870e8db11f5b66a4676',
             'a3d029beb2ce2e4f01dfe49e09f17bae9c92025f',
             'e5b2e85fb4e9c761cfe0c92b7f09ae95526a0e08',
             '104f7fd66686e41a8cdd1161e975356530fcd58a',
             '73377dbdd160cc69898caa0e97975f12172bba41',
             '07d2c6720718e498598e64f24a14b992b29bdf61',
             '92b9975e1b4449b9ea8f1be5e401fdd99a37b576',
             '4428cdf62d124df67fa87c29ace3db6906504ea4',
             'ba54ae7f42cfd11e0e1b61bb1de175052d53742b',
             '64f813de2a78fd17d898072a0d118234c1235fad']  # Latest commit
        )

    def test_discard_undesired_fixing_commits(self):
        commits = ['3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # No Ansible files modified
                   '9cbfa528b26f1d222b1b7954eef41f55d2026f4b',  # Ansible file ADDED (does not count!)
                   '9cae22d8c88d04bd19e51623ed41e8805651aaed',  # Ansible file MODIFIED (count!)
                   'e14240d8ca0ffd3ca8f093f39111d048819ab909',  # No Ansible files modified
                   '755efda3359954588c8486272b17979b3a6512a2']  # Ansible file MODIFIED (count!)

        self.miner.discard_undesired_fixing_commits(commits)

        self.assertEqual(
            commits,
            ['9cae22d8c88d04bd19e51623ed41e8805651aaed',
             '755efda3359954588c8486272b17979b3a6512a2']
        )

    def test_sort_commits(self):
        commits = ['9cbfa528b26f1d222b1b7954eef41f55d2026f4b',   # 2nd
                   '755efda3359954588c8486272b17979b3a6512a2',  # 5th
                   '3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # 1st
                   'e14240d8ca0ffd3ca8f093f39111d048819ab909',  # 4th
                   '9cae22d8c88d04bd19e51623ed41e8805651aaed']  # 3rd

        self.miner.sort_commits(commits)

        self.assertEqual(
            commits,
            ['3de3d8c2bbccf62ef5698cf33ad258aae5316432',  # 1st
             '9cbfa528b26f1d222b1b7954eef41f55d2026f4b',  # 2nd
             '9cae22d8c88d04bd19e51623ed41e8805651aaed',  # 3rd
             'e14240d8ca0ffd3ca8f093f39111d048819ab909',  # 4th
             '755efda3359954588c8486272b17979b3a6512a2']  # 5th

        )

    def test_ignore_file(self):
        self.assertFalse(self.miner.ignore_file(path_to_file='tasks/task1.yml'))
        self.assertTrue(self.miner.ignore_file(path_to_file='others/useless.py'))

    def test_get_fixing_commits(self):
        self.miner.fixing_commits = []
        commit_labels = self.miner.get_fixing_commits()

        self.assertEqual(self.miner.fixing_commits, [
            '755efda3359954588c8486272b17979b3a6512a2',
            'e7df3e45e2e27a0dc16806a834b50d0856d350fe',
            '70257245257cd899b6f26870e8db11f5b66a4676',
            '73377dbdd160cc69898caa0e97975f12172bba41',
            '07d2c6720718e498598e64f24a14b992b29bdf61',
            '4428cdf62d124df67fa87c29ace3db6906504ea4',
        ])

        self.assertDictEqual(
            commit_labels,
            {
                '755efda3359954588c8486272b17979b3a6512a2': ['CONDITIONAL'],
                'e7df3e45e2e27a0dc16806a834b50d0856d350fe': ['DOCUMENTATION', 'SYNTAX'],
                '70257245257cd899b6f26870e8db11f5b66a4676': ['DEPENDENCY', 'DOCUMENTATION', 'SERVICE'],
                '73377dbdd160cc69898caa0e97975f12172bba41': ['CONFIGURATION_DATA', 'SYNTAX'],
                '07d2c6720718e498598e64f24a14b992b29bdf61': ['CONFIGURATION_DATA'],
                '4428cdf62d124df67fa87c29ace3db6906504ea4': ['IDEMPOTENCY'],
            }
        )
        # Do sth with commit_labels

    # def test_get_fixed_files(self):
    #
    #     self.miner.get_fixing_commits()
    #     self.miner.get_fixed_files()
    #
    #     fixed_file = FixedFile(filepath='tasks/task1.yml',
    #                            fic='755efda3359954588c8486272b17979b3a6512a2',
    #                            bic='9cae22d8c88d04bd19e51623ed41e8805651aaed')
    #
    #
    #     # fixed_file = FixedFile(filepath='tasks/task2.yml',
    #     #                        fic='',
    #     #                        bic='e5b2e85fb4e9c761cfe0c92b7f09ae95526a0e08')
    #     #
    #     # fixed_file = FixedFile(filepath='tasks/task2.yml',
    #     #                        fic='',
    #     #                        bic='')
    #
    #     self.assertEqual(self.miner.fixed_files, [fixed_file])

    # def test_label(self):
    #     # Passes for commits up to: d07ed2f58c7cbabee89dbc60a62036f22c23394a
    #     self.assertEqual(self.failure_prone_files, [
    #         FailureProneFile(filepath='tasks/task1.yml',
    #                          commit='e14240d8ca0ffd3ca8f093f39111d048819ab909',
    #                          fixing_commit='755efda3359954588c8486272b17979b3a6512a2'),
    #         FailureProneFile(filepath='tasks/task1.yml',
    #                          commit='9cae22d8c88d04bd19e51623ed41e8805651aaed',
    #                          fixing_commit='755efda3359954588c8486272b17979b3a6512a2'),
    #     ])


if __name__ == '__main__':
    unittest.main()
