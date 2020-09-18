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
    description = 'A Python library to mine Infrastructure-as-Code based software repositories.'

    parser = argparse.ArgumentParser(prog='iac-repository-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + configuration.get('version', '0.0'))

    # Repository parser
    parser = subparsers.add_parser('mine-repository', help='Mine a single repository')
    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_path,
                        help='the local path to the git repository')

    parser.add_argument(action='store',
                        dest='owner',
                        type=str,
                        help='the repository owner')

    parser.add_argument(action='store',
                        dest='repo_name',
                        type=str,
                        help='the repository name')

    parser.add_argument(action='store',
                        dest='dest',
                        type=valid_path,
                        help='destination folder for the report')

    parser.add_argument('--branch',
                         action='store',
                         dest='branch',
                         type=str,
                         default='master',
                         help='the repository branch to mine (default: %(default)s)')

    parser.add_argument('--verbose',
                         action='store_true',
                         dest='verbose',
                         default=False,
                         help='show log')

    return parser


def main():

    args = get_parser().parse_args()

    load_dotenv()

    token = os.getenv('GITHUB_ACCESS_TOKEN')
    if not token:
        token = getpass('Github access token:')

    if args.verbose:
        print(f'Mining: {args.path_to_repo} [{datetime.now().hour}:{datetime.now().minute}]')

    miner = RepositoryMiner(token=token,
                            path_to_repo=args.path_to_repo,
                            branch=args.branch,
                            owner=args.owner,
                            repo=args.name)

    metrics_df = pd.DataFrame()

    for metrics in miner.mine():
        metrics_df = metrics_df.append(metrics, ignore_index=True)

    if args.verbose:
        print(f'Saving results in {args.dest}/metrics.csv')

    metrics_df.to_csv(os.path.join(args.dest, 'metrics.csv'), mode='w', index=False)

    if args.verbose:
        print(f'Mining ended at: {datetime.now().hour}:{datetime.now().minute}')

    exit(0)


