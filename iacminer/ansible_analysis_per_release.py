"""
Analyze all repositories in data/ansible_repositories
"""
import os, sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

import argparse
import pandas

from iacminer.mine_repo import MineRepo 
from iacminer.utils import load_filtered_ansible_repositories
from progress.bar import Bar

def main(labeler:int=1):
    
    repositories = load_filtered_ansible_repositories()
    print(repositories)
    
    bar = Bar('Processing', max=len(repositories), fill='=')
    exit()
    i = 0
    for repo in repositories:
        print(f'\n{repo}')

        i += 1

        if i <= 4:
            bar.next()
            continue

        dst = os.path.join('data', 'release', f'{repo.replace("/", "_")}.csv')
        
        dataset = pandas.DataFrame()
    
        for metrics in MineRepo(repo, labeler=1, language='ansible', branch=repo['default_branch']).start():

            dataset = dataset.append(metrics, ignore_index=True)

            with open(dst, 'w') as out:
                dataset.to_csv(out, mode='w', index=False)
        
        bar.next()

    bar.finish()


def getParser():
    
    parser = argparse.ArgumentParser(prog='iac-miner')
    parser.add_argument(action='store',
                        dest='labeler',
                        choices=['1','2'],
                        default='2')

    return parser

if __name__=='__main__':

    main(labeler=1)