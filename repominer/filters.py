def is_ansible_file(path: str) -> bool:
    """
    Check whether the path is an Ansible file
    :param path: a path
    :return: True if the path links to an Ansible file. False, otherwise
    """
    return path and ('test' not in path) and any(w in path for w in ['playbooks/', 'meta/', 'tasks/', 'handlers/', 'roles/']) and path.endswith('.yml')


def is_tosca_file(path: str, content: str = None) -> bool:
    """
    Check whether the path is a TOSCA file
    :param path: a path
    :param content: eventually the source code
    :return: True if the path links to a TOSCA file. False, otherwise
    """
    if content:
        return 'tosca_definitions_version' in content

    return path and ('test' not in path) and any(path.endswith(ext) for ext in ['.tosca', '.tosca.yaml', '.tosca.yml'])
