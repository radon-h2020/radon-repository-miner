import os
import shutil
import unittest

from repominer.mining.tosca import ToscaMiner


class ToscaMinerTestSuite(unittest.TestCase):

    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

        cls.miner = ToscaMiner(
            url_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing.git',
            clone_repo_to=os.path.join(os.getcwd(), 'test_data', 'tmp'),
            branch='origin/test-tosca-miner'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_discard_undesired_fixing_commits(self):
        commits = [
            '1742ca7dcbbcff0c5ac116e472a5cda2ac7fb307',  # No Tosca files modified
            'd6ed6b7d589b40292bdce0b1bdb293687fa010a0',  # Tosca file ADDED (does not count!)
            'e4e4ddce273b22379ac34f8208f0b9af11b0bebb',  # Ansible file MODIFIED (count!)
        ]

        self.miner.discard_undesired_fixing_commits(commits)

        self.assertEqual(
            commits,
            ['1742ca7dcbbcff0c5ac116e472a5cda2ac7fb307']
        )

    def test_ignore_file(self):

        content = 'tosca_definitions_version: alien_dsl_1_4_0\nmetadata:\n\ttemplate_name: ' \
                  'org.alien4cloud.automation.cloudify.topologies.hostpool_as_a_service\n\ttemplate_version: ' \
                  '1.4.0-SNAPSHOT\n\ttemplate_author: alien4cloud\n'

        self.assertFalse(self.miner.ignore_file(path_to_file='service.tosca'))
        self.assertFalse(self.miner.ignore_file(path_to_file='service.tosca.yaml'))
        self.assertFalse(self.miner.ignore_file(path_to_file='service.yml', content=content))
        self.assertTrue(self.miner.ignore_file(path_to_file='service.yml'))
        self.assertTrue(self.miner.ignore_file(path_to_file='useless.py'))


if __name__ == '__main__':
    unittest.main()
