"""
Analyze all repositories in data/ansible_repositories
"""
import os, sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

import argparse
import pandas

from iacminer.mine_repo import MineRepo 
from iacminer.utils import load_ansible_repositories
from progress.bar import Bar

def main(labeler:int=1):
    
    repositories = load_ansible_repositories()
    bar = Bar('Processing', max=len(repositories), fill='=')
    
    i = 0
    for repo in repositories:
        print(f'\n{repo["owner"]}_{repo["name"]}')

        i += 1

        if i <= 25:
            bar.next()
            continue

        if labeler == 1:
            dst = os.path.join('data', 'release', f'{repo["owner"]}_{repo["name"]}.csv')
        else:
            dst = os.path.join('data', 'commit', f'{repo["owner"]}_{repo["name"]}.csv')
        
        dataset = pandas.DataFrame()

        for metrics in MineRepo(f'{repo["owner"]}/{repo["name"]}', labeler=labeler, language='ansible', branch=repo['default_branch']).start():

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

    parser = getParser()
    args = parser.parse_args()
    
    main(labeler=1 if args.labeler == '1' else 2)