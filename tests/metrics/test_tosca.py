import os
import unittest
import shutil

from repominer.metrics.tosca import ToscaMetricsExtractor


class BaseMetricsExtractorTestSuite(unittest.TestCase):
    path_to_tmp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)

        cls.me = ToscaMetricsExtractor(path_to_repo='https://github.com/stefanodallapalma/radon-repository-miner-testing',
                                       clone_repo_to=cls.path_to_tmp_dir,
                                       at='release')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)

    def test_get_product_metrics(self):
        content = 'tosca_definitions_version: alien_dsl_1_4_0\nmetadata:\n\ttemplate_name: ' \
                  'org.alien4cloud.automation.cloudify.topologies.hostpool_as_a_service\n\ttemplate_version: ' \
                  '1.4.0-SNAPSHOT\n\ttemplate_author: alien4cloud\n'.expandtabs(2)

        self.assertEqual(self.me.get_product_metrics(script=content).keys(), {
            'lines_code',
            'lines_blank',
            'num_keys',
            'num_tokens',
            'text_entropy',
            'num_parameters',
            'num_suspicious_comments',
            'num_imports',
            'num_inputs',
            'num_interfaces',
            'num_node_templates',
            'num_node_types',
            'num_properties',
            'num_relationship_templates',
            'num_relationship_types',
            'num_shell_scripts'
        })

    def test_get_product_metrics_type_error(self):
        content = '---\n- name: Copy WAR file to host (invalid)\n\tcopy:\n\t\tsrc: helloworld.war\n\t\tdest: /tmp\n'
        self.assertEqual(len(self.me.get_product_metrics(script=content)), 0)

    def test_ignore_file(self):

        content = 'tosca_definitions_version: alien_dsl_1_4_0\nmetadata:\n\ttemplate_name: ' \
                  'org.alien4cloud.automation.cloudify.topologies.hostpool_as_a_service\n\ttemplate_version: ' \
                  '1.4.0-SNAPSHOT\n\ttemplate_author: alien4cloud\n'

        self.assertFalse(self.me.ignore_file(path_to_file='service.tosca'))
        self.assertFalse(self.me.ignore_file(path_to_file='service.tosca.yaml'))
        self.assertFalse(self.me.ignore_file(path_to_file='service.yml', content=content))
        self.assertTrue(self.me.ignore_file(path_to_file='service.yml'))
        self.assertTrue(self.me.ignore_file(path_to_file='useless.py'))



if __name__ == '__main__':
    unittest.main()
