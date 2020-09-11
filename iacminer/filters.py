def is_ansible_repository(owner:str, name:str, description:str, root_dirs:list) -> bool:
    """
    Check if the repository has Ansible files
    :param owner: the repository's owner
    :param name: the repository's name
    :param description: the repository's description
    :param root_dirs: a list of directory names at the root of the repository
    :return: True if the repository has Ansible files; False otherwise
    """
    return 'ansible' in description.lower() \
           or 'ansible' in owner.lower() \
           or 'ansible' in name.lower() \
           or sum([1 for path in root_dirs if is_ansible_dir(path)]) >= 2


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


