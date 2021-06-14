import unittest

from repominer import filters


class TestFiltersTestSuite(unittest.TestCase):

    def test_is_ansible_file_true(self):
        assert filters.is_ansible_file('playbooks/task.yml')
        assert filters.is_ansible_file('meta/task.yml')
        assert filters.is_ansible_file('tasks/task.yml')
        assert filters.is_ansible_file('handlers/task.yml')
        assert filters.is_ansible_file('roles/task.yml')

    def test_is_ansible_file_false(self):
        assert not filters.is_ansible_file('test/task.yml')
        assert not filters.is_ansible_file('repominer/task.yml')

    def test_is_tosca_file_true(self):
        assert filters.is_tosca_file('service.tosca')
        assert filters.is_tosca_file('service.tosca.yaml')
        assert filters.is_tosca_file('service.tosca.yml')

        content = 'tosca_definitions_version: alien_dsl_1_4_0\nmetadata:\n\ttemplate_name: ' \
                  'org.alien4cloud.automation.cloudify.topologies.hostpool_as_a_service\n\ttemplate_version: ' \
                  '1.4.0-SNAPSHOT\n\ttemplate_author: alien4cloud\n '

        assert filters.is_tosca_file('service.yml', content=content)

    def test_is_tosca_file_false(self):
        assert not filters.is_tosca_file('test/service.tosca')
        assert not filters.is_tosca_file('service.yaml', content=None)

        content = '- definition: alien4cloud.tosca.model.ArchiveRoot\n\ttosca_definitions_version: ' \
                  'archive.toscaDefinitionsVersion '

        assert not filters.is_tosca_file('service.yml', content=content)


if __name__ == '__main__':
    unittest.main()
