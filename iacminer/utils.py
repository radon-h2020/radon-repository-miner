import csv
import json
import os
import re

from iacminer.entities.file import LabeledFile

def load_filtered_ansible_repositories():
    repos = []
    
    path = os.path.join('data', 'filtered_ansible_repositories.csv')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            reader = csv.reader(in_file)
            next(reader)
            
            for row in reader:
                repo = re.match(r'https://github.com/(.+/.+)', row[0]).group(1)
                repos.append(repo)
            
    return repos

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


def load_labeled_files():
    path = os.path.join('data', 'labeled_files.json')
    if os.path.isfile(path):
        with open(path, 'r') as in_file:
            return json.load(in_file) 
    
    return []

def save_labeled_file(repo: str, labeled_file: LabeledFile):
    file = dict(repo=str(repo),
                filepath=str(labeled_file.filepath),
                commit=str(labeled_file.commit),
                label=str(labeled_file.label.value),
                ref=str(labeled_file.ref))

    files = load_labeled_files()
    files.append(file)

    path = os.path.join('data', 'labeled_files.json')
    with open(path, 'w') as outfile:
        return json.dump(files, outfile)
