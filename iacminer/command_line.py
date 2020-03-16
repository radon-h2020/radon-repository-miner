import os, sys
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(path)

import argparse
from datetime import datetime
from iacminer.mine_repo import MineRepo

import pandas as pd

def unsigned_int(x):
    x = int(x)
    if x < 0:
        raise argparse.ArgumentTypeError('Minimum bound is 0')
    return x

def date(x):
    
    try:
        # String to datetime
        x = datetime.strptime(x, '%Y-%m-%d')
    except Exception:
        raise argparse.ArgumentTypeError('Date format must be: yyyy-mm-dd')
    
    return x

def repo_name(x):
    
    if len(x.split('/')) != 2:
        raise argparse.ArgumentTypeError('The name of the repository must be: owner/name')
    
    return x

def getParser():
    description='IaC-Miner allows for ...'
    
    parser = argparse.ArgumentParser(prog='iac-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Github subparser
    github_parser = subparsers.add_parser('mine-github', help='To extract repositories from Github')
    github_parser.add_argument('--from',
                        action='store',
                        dest='date_from',
                        type=date,
                        default=datetime.strptime('2014-01-01', '%Y-%m-%d'),
                        help='Start searching from this date (default 2014-01-01).')

    github_parser.add_argument('--to',
                        action='store',
                        dest='date_to',
                        type=date,
                        default=datetime.strptime('2020-01-01', '%Y-%m-%d'),
                        help='Search up to this date (default 2020-01-01).')

    github_parser.add_argument('--pushed-after',
                        action='store',
                        dest='date_push',
                        type=date,
                        default=datetime.strptime('2019-01-01', '%Y-%m-%d'),
                        help='Search up to this date (default 2019-01-01).')

    github_parser.add_argument('--releases',
                        action='store',
                        dest='releases',
                        type=unsigned_int,
                        default=0,
                        help='Minimum number of releases.')
    
    github_parser.add_argument('--stars',
                        action='store',
                        dest='stars',
                        type=unsigned_int,
                        default=0,
                        help='Minimum number of stars.')

    github_parser.add_argument('--include-archived',
                        action='store_true',
                        dest='include_archived',
                        default=False,
                        help='To include archived repositories.')

    github_parser.add_argument('--include-fork',
                        action='store_true',
                        dest='include_fork',
                        default=False,
                        help='To include archived repositories.')

    github_parser.add_argument('--include-mirrors',
                        action='store_true',
                        dest='include_mirror',
                        default=False,
                        help='To include mirror repositories.')
    
    # MINE-REPOs
    repos_parser = subparsers.add_parser('mine-repo', help='To extract scripts from a repository')
    repos_parser.add_argument(action='store',
                              dest='repository',
                              type=repo_name,
                              help='Name of the repository (owner/name).')

    repos_parser.add_argument('--labeler',
                        action='store',
                        dest='labeler',
                        choices=['1','2'],
                        default='2',
                        help='The labeling technique. Can be\n \
                              (1) to label scripts as "clean" from start to first buggy inducing commit (exlucsive), and "defective" from the fisrt buggy inducing commit (inclusive) to the fixing commit (exclusive); \
                              or (2) to label scripts as "defective" only at each buggy inducing commit, and "clean" on all other commits.')

    repos_parser.add_argument('--language',
                        action='store',
                        dest='language',
                        choices=['ansible'],
                        default='ansible',
                        help='Mine only files of this language.')

    return parser

if __name__=='__main__':

    parser = getParser()
    args = parser.parse_args()
    
    if args.command == 'mine-github':
        print('MINING GITHUB')
        print(args)
        # TODO: mine_github.main()
    elif args.command == 'mine-repo':
        print(args)
        print('MINING REPOS')

        dest = os.path.join('data', 'metrics_just_in_time.csv')

        dataset = pd.DataFrame()
        # Load dataframe, if exists
        if os.path.isfile('data'):
            with open(dest, 'r') as in_file:
                dataset = pd.read_csv(in_file)

        for metrics in MineRepo(args.repository, int(args.labeler), args.language).start():
            # Update dataframe
            dataset = dataset.append(metrics, ignore_index=True)

            # Save to csv
            with open(dest, 'w') as out:
                dataset.to_csv(out, mode='w', index=False)

        print('Done!')