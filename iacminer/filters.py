def is_ansible_dir(path: str) -> bool:
    """
    Verify if a path is an Ansible directory
    
    Parameters
    ----------
    path : str: the to analyze

    Return
    ----------
    bool : True if the path is an Ansible directory, False otherwise
    """

    return path and ('playbooks'==path or 'meta'==path or 'tasks'==path or 'handlers'==path or 'roles'==path)

def is_ansible_file(path: str) -> bool:
    """
    Verify if a path is an Ansible file
    
    Parameters
    ----------
    path : str: the to analyze

    Return
    ----------
    bool : True if the path is an Ansible file, False otherwise
    """
    return path and ('test' not in path) and ('playbooks' in path or 'meta' in path or 'tasks' in path or 'handlers' in path or 'roles' in path) and path.endswith('.yml')