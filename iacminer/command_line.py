import argparse
import json
import os
import pandas as pd

import copy
from datetime import datetime
from dotenv import load_dotenv
from iacminer import filters
from iacminer import utils
from iacminer.miners.github import GithubMiner
from iacminer.miners.repository import RepositoryMiner
from iacminer.mongo import MongoDBManager
from iacminer.report import generate_mining_report
from repositoryscorer import scorer

with open('config.json', 'r') as in_stream:
    configuration = json.load(in_stream)


def date(x: str) -> datetime:
    """
    Check the passed date is well-formatted
    :param x: a datetime
    :return: datetime(x); raise an ArgumentTypeError otherwise
    """
    try:
        # String to datetime
        x = datetime.strptime(x, '%Y-%m-%d')
    except Exception:
        raise argparse.ArgumentTypeError('Date format must be: YYYY-MM-DD')

    return x


def unsigned_int(x: str) -> int:
    """
    Check the number is greater than or equal to zero
    :param x: a number
    :return: int(x); raise an ArgumentTypeError otherwise
    """
    x = int(x)
    if x < 0:
        raise argparse.ArgumentTypeError('Minimum bound is 0')
    return x


def valid_path(x: str) -> str:
    """
    Check the path exists
    :param x: a path
    :return: the path if exists; raise an ArgumentTypeError otherwise
    """
    if not os.path.isdir(x):
        raise argparse.ArgumentTypeError('Insert a valid path')

    return x


def get_parser():
    description = 'A Python library to crawl GitHub for Infrastructure-as-Code based repositories and mine' \
                  'those repositories to identify fixing commits and label defect-prone files.'

    parser = argparse.ArgumentParser(prog='iac-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + configuration.get('version', '0.0'))

    subparsers = parser.add_subparsers(dest='command')

    # Github parser
    github_parser = subparsers.add_parser('mine-github', help='Mine repositories from Github')

    github_parser.add_argument(action='store',
                               dest='mongodb_host',
                               type=str,
                               help='the MongoDB host (e.g., "127.0.0.1")',
                               default='localhost')

    github_parser.add_argument(action='store',
                               dest='mongodb_port',
                               type=unsigned_int,
                               help='the MongoDB port (e.g., 27017)',
                               default=27017)

    github_parser.add_argument(action='store',
                               dest='dest',
                               type=valid_path,
                               help='destination folder to save results')

    github_parser.add_argument(action='store',
                               dest='clone_to',
                               type=valid_path,
                               help='path to temporary clone the repositories for the analysis')

    github_parser.add_argument('--from',
                               action='store',
                               dest='date_from',
                               type=date,
                               default=datetime.strptime('2014-01-01', '%Y-%m-%d'),
                               help='start searching from this date (default: %(default)s)')

    github_parser.add_argument('--to',
                               action='store',
                               dest='date_to',
                               type=date,
                               default=datetime.strptime('2020-01-01', '%Y-%m-%d'),
                               help='search up to this date (default: %(default)s)')

    github_parser.add_argument('--pushed-after',
                               action='store',
                               dest='date_push',
                               type=date,
                               default=datetime.strptime('2019-01-01', '%Y-%m-%d'),
                               help='search up to this date (default: %(default)s)')

    github_parser.add_argument('--min-issues',
                               action='store',
                               dest='min_issues',
                               type=unsigned_int,
                               default=0,
                               help='minimum number of issues (default: %(default)s)')

    github_parser.add_argument('--min-releases',
                               action='store',
                               dest='min_releases',
                               type=unsigned_int,
                               default=0,
                               help='minimum number of releases (default: %(default)s)')

    github_parser.add_argument('--min-stars',
                               action='store',
                               dest='min_stars',
                               type=unsigned_int,
                               default=0,
                               help='minimum number of stars (default: %(default)s)')

    github_parser.add_argument('--min-watchers',
                               action='store',
                               dest='min_watchers',
                               type=unsigned_int,
                               default=0,
                               help='minimum number of watchers (default: %(default)s)')

    github_parser.add_argument('--verbose',
                               action='store_true',
                               dest='verbose',
                               default=False,
                               help='whether to output results (default: %(default)s)')

    # Repository parser
    repo_parser = subparsers.add_parser('mine-repository', help='Mine a single repository')
    repo_parser.add_argument(action='store',
                             dest='path_to_repo',
                             type=valid_path,
                             help='Name of the repository (owner/name).')

    repo_parser.add_argument(action='store',
                             dest='dest',
                             type=valid_path,
                             help='Destination folder to save results.')

    repo_parser.add_argument('--branch',
                             action='store',
                             dest='repo_branch',
                             type=str,
                             default='master',
                             help='the repository\'s default branch (default: %(default)s)')

    repo_parser.add_argument('--name',
                             action='store',
                             dest='repo_name',
                             type=str,
                             default=None,
                             help='the repository\'s name (default: %(default)s)')

    repo_parser.add_argument('--owner',
                             action='store',
                             dest='repo_owner',
                             type=str,
                             default=None,
                             help='the repository\'s owner (default: %(default)s)')

    repo_parser.add_argument('--verbose',
                             action='store_true',
                             dest='verbose',
                             default=False,
                             help='whether to output results (default: %(default)s)')

    return parser


def is_ansible(repository: dict) -> bool:
    """
    Check if the repository has Ansible files
    :param repository: a json object containing "owner", "name", "description" and "dirs" for the repository
    :return: True if the repository has Ansible files; False otherwise
    """
    return 'ansible' in repository['description'].lower() \
           or 'ansible' in repository['owner'].lower() \
           or 'ansible' in repository['name'].lower() \
           or sum([1 for path in repository['dirs'] if filters.is_ansible_dir(path)]) >= 2


def mine_github(args):
    load_dotenv()

    db_manager = MongoDBManager(args.mongodb_host, args.mongodb_port)

    github_miner = GithubMiner(
        access_token=os.getenv('GITHUB_ACCESS_TOKEN'),
        date_from=args.date_from,
        date_to=args.date_to,
        pushed_after=args.date_push,
        min_stars=args.min_stars,
        min_releases=args.min_releases,
        min_watchers=args.min_watchers,
        min_issues=args.min_issues
    )

    for repository in github_miner.mine():

        # Filter out non-Ansible repositories
        if not is_ansible(repository):
            continue

        if args.verbose:
            print(f'Collecting {repository["url"]} ... ', end='', flush=True)

        # Save repository to MongoDB
        if db_manager.get_single_repo(repository['_id']):
            db_manager.replace_repo(repository)
        else:
            db_manager.add_repo(repository)

        if args.verbose:
            print('DONE')

    # Generate html report
    report = generate_mining_report(db_manager.get_all_repos())
    destination = os.path.join(args.dest, 'report.html')
    with open(destination, 'w') as out:
        out.write(report)

    if args.verbose:
        print(f'Report created at {destination}')

    exit(0)


def mine_repository(args):
    if args.verbose:
        print(f'Mining started at: {datetime.now().hour}:{datetime.now().minute}')

    path_to_repo = args.path_to_repo

    miner = RepositoryMiner(token=os.getenv('GITHUB_ACCESS_TOKEN'),
                            path_to_repo=path_to_repo,
                            branch=args.repo_branch,
                            owner=args.repo_owner,
                            repo=args.repo_name)

    metrics_df = pd.DataFrame()

    for metrics in miner.mine():
        metrics_df = metrics_df.append(metrics, ignore_index=True)

    if args.verbose:
        print(f'Saving results in {args.dest}/metrics.csv')

    metrics_df.to_csv(os.path.join(args.dest, 'metrics.csv'), mode='w', index=False)

    if args.verbose:
        print(f'Mining ended at: {datetime.now().hour}:{datetime.now().minute}')


def cli():
    args = get_parser().parse_args()

    if args.command == 'mine-github':
        mine_github(args)

    elif args.command == 'mine-repository':
        mine_repository(args)

""" REPOSITORY SCORER
 try:
     # Clone repository
     if args.verbose:
         print(f'Cloning {repository["url"]}')

     path_to_repository = utils.clone_repository(os.path.join(args.clone_to), repository['url'])

     if args.verbose:
         print(f'Cloned to {path_to_repository}')

     if args.verbose:
         print('Computing repository scores')

     scores = scorer.score_repository(path_to_repo=path_to_repository,
                                      threshold_community=2,
                                      threshold_comments_ratio=0.002,
                                      threshold_commit_frequency=2,
                                      threshold_issue_events=0.023,
                                      threshold_sloc=190)
     repository.update(scores)
     repository.update({'timestamp': datetime.now().timestamp()})

     # Delete cloned repository
     if args.verbose:
         print(f'Deleting {path_to_repository}')

     utils.delete_repo(path_to_repository)

 except Exception as e:
     print(str(e))
     utils.delete_repo(path_to_repository)
     continue
 """