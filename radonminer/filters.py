import re
pattern_tosca_definitions = re.compile('tosca_definitions_version\s*:')


def is_ansible_file(path: str) -> bool:
    """
    Check whether the path is an Ansible file
    :param path: a path
    :return: True if the path links to an Ansible file. False, otherwise
    """
    return path and ('test' not in path) \
           and ('ansible' in path or 'playbooks' in path or 'meta' in path or 'tasks' in path or 'handlers' in path or 'roles' in path) \
           and path.endswith('.yml')


def is_tosca_file(path: str, content:str=None) -> bool:
    """
    Check whether the path is a TOSCA file
    :param path: a path
    :param content: eventually the source code
    :return: True if the path links to a TOSCA file. False, otherwise
    """
    if content:
        return pattern_tosca_definitions.match(content) is not None

    return path and ('test' not in path) and (path.endswith('.tosca') or path.endswith('.tosca.yaml'))
