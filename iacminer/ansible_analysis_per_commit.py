"""
Analyze all repositories in data/ansible_repositories
"""
import os, sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

import pandas

from iacminer.mine_repo import MineRepo 
from iacminer.utils import load_ansible_repositories
from progress.bar import Bar

def main():
    
    repositories = load_ansible_repositories()
    bar = Bar('Processing', max=len(repositories), fill='=')
    
    i = 0
    for repo in repositories:
        print(f'\n{repo["owner"]}_{repo["name"]}')

        i += 1

        if i <= 602:
            bar.next()
            continue

        dst = os.path.join('data', 'commit', f'{repo["owner"]}_{repo["name"]}.csv')
        
        dataset = pandas.DataFrame()

        for metrics in MineRepo(f'{repo["owner"]}/{repo["name"]}', labeler=2, language='ansible', branch=repo['default_branch']).start():

            dataset = dataset.append(metrics, ignore_index=True)

            with open(dst, 'w') as out:
                dataset.to_csv(out, mode='w', index=False)
        
        bar.next()

    bar.finish()


if __name__=='__main__':

    main()