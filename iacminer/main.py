import json
import os
import pandas as pd
import sys
import yaml

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

from io import StringIO

from iacminer.entities.release import Release
from iacminer.miners.commits import CommitsMiner
from iacminer.miners.metrics import MetricsMiner
from iacminer.miners.scripts import ScriptsMiner
from iacminer.utils import load_repositories


import git
import shutil
from pathlib import Path
from pydriller.repository_mining import GitRepository


DESTINATION_PATH = os.path.join('data', 'metrics_new.csv')


def clone_repo(repo: str):
     # Clone repo
    author = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    root_path = str(Path(f'repositories/{author}'))
    repo_path = os.path.join(root_path, repo_name)
    
    delete_repo(root_path)
    os.makedirs(root_path)

    git.Git(root_path).clone(f'https://github.com/{repo}.git', branch='master')
    git_repo = GitRepository(repo_path)
    
    return git_repo
    

def main():

    repos = load_repositories()
    
    for repo in repos:

        print(f'Mining repository: {repo}')
        
        # Clone repo
        git_repo = clone_repo(repo)
        commits_miner = CommitsMiner(git_repo)
        scripts_miner = ScriptsMiner(git_repo)
        metrics_miner = MetricsMiner()
        process_metrics = {}

        buggy_inducing_commits = commits_miner.mine()
        # TODO: save buggy inducing commits to json

        releases = []

        for commit in buggy_inducing_commits:
            r = Release(commit.release_starts_at, commit.release_ends_at)
            r.defective_filepaths = commit.release_filepaths
            r.repo = commit.repo
            r.date = str(commit.release_date)
            r.buggy_inducing_commits.add(commit)
            
            if r not in releases:
                releases.append(r)
            else:
                idx = releases.index(r)
                releases[idx].defective_filepaths.union(r.defective_filepaths)
                releases[idx].buggy_inducing_commits.add(commit)

        for release in releases:
 
            if not release.defective_filepaths:
                continue
          
            print(f'Analyzing release: [{release.start}, {release.end}]')
            
            process_metrics = metrics_miner.mine_process_metrics(str(git_repo.path), release.start, release.end)
            git_repo.checkout(release.end)

            for content in scripts_miner.mine(release):
                metadata = {
                    'repo': release.repo,
                    'release_start': release.start,
                    'release_end': release.end,
                    'release_date': release.date,
                    'filepath': content.filepath,
                    'defective': 'yes' if content.defective else 'no'
                }

                product_metrics = metrics_miner.mine_product_metrics(content.content)
                save(content.filepath, metadata, process_metrics, product_metrics)

            git_repo.reset()

        git_repo.clear()

        author = repo.split('/')[0]
        root_path = str(Path(f'repositories/{author}'))
        delete_repo(root_path)

def delete_repo(path_to_repo: str):
    # delete local repo
    if os.path.isdir(path_to_repo):
        shutil.rmtree(path_to_repo)

def save(filepath:str, metadata:dict, process_metrics:dict, product_metrics:dict):
        """
        :filepath: str - the filepath for the process metrics
        """
        
        filepath = str(Path(filepath))
        
        metrics = metadata
        metrics.update(product_metrics)

        # Saving process metrics
        metrics['commits_count'] = process_metrics[0].get(filepath, 0)

        if not metrics['commits_count'] and metadata["defective"] == 'yes':
            print()
            print(f'Process metrics for release: {metadata["release_ends_at"]}:\n{process_metrics}')
            print(f'Commits count for release perriod: [{metadata["release_starts_at"]}, {metadata["release_ends_at"]}]:\n{process_metrics[0]}')
            print()
            print(f'filepath: {filepath}')
            print(f'defective: {metadata["defective"]}')
            exit()

        metrics['contributors_count'] = process_metrics[1].get(filepath, {}).get('contributors_count', 0)
        metrics['minor_contributors_count'] = process_metrics[1].get(filepath, {}).get('minor_contributors_count', 0)
        metrics['highest_experience'] = process_metrics[2].get(filepath, 0)
        metrics['highest_experience'] = process_metrics[3].get(filepath, 0)
        metrics['median_hunks_count'] = process_metrics[4].get(filepath, 0)
        metrics['total_added_loc'] = process_metrics[5].get(filepath, {}).get('added', 0)
        metrics['total_removed_loc'] = process_metrics[5].get(filepath, {}).get('removed', 0)
        #metrics['norm_added_loc'] = process_metrics[6].get(filepath, {}).get('added', 0)
        #metrics['norm_removed_loc'] = process_metrics[6].get(filepath, {}).get('removed', 0)

        #if metrics['total_added_loc'] and metrics['norm_added_loc']:
        #    metrics['norm_added_loc'] /= metrics['total_added_loc']
        #    metrics['norm_added_loc'] = round(100 * metrics['norm_added_loc'], 2)
        
        #if metrics['total_removed_loc'] and metrics['norm_removed_loc']:
        #    metrics['norm_removed_loc'] /= metrics['total_removed_loc']
        #    metrics['norm_removed_loc'] = round(100 * metrics['norm_removed_loc'], 2)

        dataset = pd.DataFrame()
        
        if os.path.isfile(DESTINATION_PATH):
            with open(DESTINATION_PATH, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        dataset = dataset.append(metrics, ignore_index=True)

        with open(DESTINATION_PATH, 'w') as out:
            dataset.to_csv(out, mode='w', index=False)



if __name__=='__main__':
    main()