def is_ansible_dir(path: str) -> bool:
    """
    Check whether the path is an Ansible directory
    :param path: a path
    :return: True if the path link to an Ansible directory. False, otherwise
    """
    return path and ('playbooks' == path or 'meta' == path or 'tasks' == path or 'handlers' == path or 'roles' == path)


def is_ansible_file(path: str) -> bool:
    """
    Check whether the path is an Ansible file
    :param path: a path
    :return: True if the path link to an Ansible file. False, otherwise
    """
    return path and ('test' not in path) \
           and ('ansible' in path or 'playbooks' in path or 'meta' in path or 'tasks' in path or 'handlers' in path or 'roles' in path) \
           and path.endswith('.yml')


