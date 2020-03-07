import argparse
from datetime import datetime

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
                        help='Start searching from this date (default 2014-01-01)')

    github_parser.add_argument('--to',
                        action='store',
                        dest='date_to',
                        type=date,
                        default=datetime.strptime('2020-01-01', '%Y-%m-%d'),
                        help='Search up to this date (default 2020-01-01)')

    github_parser.add_argument('--pushed-after',
                        action='store',
                        dest='date_push',
                        type=date,
                        default=datetime.strptime('2019-01-01', '%Y-%m-%d'),
                        help='Search up to this date (default 2019-01-01)')

    github_parser.add_argument('--releases',
                        action='store',
                        dest='releases',
                        type=unsigned_int,
                        default=0,
                        help='Minimum number of releases')
    
    github_parser.add_argument('--stars',
                        action='store',
                        dest='stars',
                        type=unsigned_int,
                        default=0,
                        help='Minimum number of stars')

    github_parser.add_argument('--include-archived',
                        action='store_true',
                        dest='include_archived',
                        default=False,
                        help='To include archived repositories')

    github_parser.add_argument('--include-fork',
                        action='store_true',
                        dest='include_fork',
                        default=False,
                        help='To include archived repositories')

    github_parser.add_argument('--include-mirrors',
                        action='store_true',
                        dest='include_mirror',
                        default=False,
                        help='To include mirror repositories')
    
    repos_parser = subparsers.add_parser('mine-repos', help='To extract scripts from repositories')
    repos_parser.add_argument('--from',
                        action='store',
                        dest='date_from',
                        type=date,
                        default=datetime.strptime('2014-01-01', '%Y-%m-%d'),
                        help='Start searching from this date (default 2014-01-01)')

    return parser

if __name__=='__main__':

    parser = getParser()
    #args = parser.parse_args(['mine-github'])
    args = parser.parse_args()
    
    if args.command == 'mine-github':
        print('MINING GITHUB')
        print(args)
    elif args.command == 'mine-repos':
        print('MINING REPOS')