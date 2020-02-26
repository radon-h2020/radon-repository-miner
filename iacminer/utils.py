import json
import os

from iacminer.entities.repository import RepositoryEncoder, RepositoryDecoder

def load_ansible_repositories():
    path = os.path.join('data', 'ansible_repositories.json')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            return json.load(in_file, cls=RepositoryDecoder) 
    
    return []

def save_ansible_repositories(repositories: list):

    dict_repos = []
    for r in repositories:
        dict_repos.append(r.__dict__) 

    path = os.path.join('data', 'ansible_repositories.json')
    with open(path, 'w') as outfile:
        return json.dump(repositories, outfile, cls=RepositoryEncoder)

def difference(list1, list2):
    new_list = []
    new_list.extend([j for j in list1 if j not in list2])
    new_list.extend([j for j in list2 if j not in list1])
    return new_list