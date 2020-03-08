import json
import os

def load_ansible_repositories():
    path = os.path.join('data', 'ansible_repositories.json')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            return json.load(in_file) 
    
    return []

def save_ansible_repository(repo: dict):

    repos = load_ansible_repositories()
    repos.append(repo)

    path = os.path.join('data', 'ansible_repositories.json')
    with open(path, 'w') as outfile:
        return json.dump(repos, outfile)


def load_fixging_commits():
    path = os.path.join('data', 'fixing_commits.json')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            return json.load(in_file) 
    
    return []

def save_fixing_commits(repo: str, fixing_commits: set):

    commits = load_fixging_commits()
    commits.append({
        'repo': repo,
        'fixing_commits': list(fixing_commits)
    })

    path = os.path.join('data', 'fixing_commits.json')
    with open(path, 'w') as outfile:
        return json.dump(commits, outfile)