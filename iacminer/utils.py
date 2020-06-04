import git
import os
import re
import shutil

def clone_repository(path_to_folder: str, url_to_repo: str) -> str:
    """
    Clone a repository in the specified folder
    :param path_to_folder: the folder where to clone the repository
    :param url_to_repo: the url to the repository,
    :return: the path to the local repository
    """
    match = re.match(r'(https:\/\/)?github\.com\/(.+)\/(.+)(\.git)?', url_to_repo)
    if not match:
        raise ValueError('Not a valid Github url')

    owner, name = match.groups()[1], match.groups()[2]

    path_to_owner = os.path.join(path_to_folder, owner)
    if not os.path.isdir(path_to_owner):
        os.makedirs(path_to_owner)

    git.Git(path_to_owner).clone(url_to_repo)
    return os.path.join(path_to_owner, name)


def delete_repo(path_to_repo: str) -> None:
    """
    Delete a local repository.
    :param path_to_repo: path to the repository to delete
    :return: None
    """
    try:
        path_to_owner = '/'.join(path_to_repo.split('/')[:-1])
        if len(os.listdir(path_to_owner)) == 1:
            shutil.rmtree(path_to_owner)
        else:
            shutil.rmtree(path_to_repo)

    except Exception as e:
        print(f'>>> Error while deleting directory: {str(e)}')

