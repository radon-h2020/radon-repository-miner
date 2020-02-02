def is_ansible_file(filepath: str) -> bool:
    """ 
    Return True if the file is supposed to be an Ansible file, False otherwise
    :filepath: the path of the file to analyze
    :return: bool
    """
    return filepath and ('playbooks' in filepath or 'meta' in filepath or 'tasks' in filepath or 'handlers' in filepath or 'roles' in filepath) and filepath.endswith('.yml')
