import argparse
import copy
import io
import json
import os

from datetime import datetime
from getpass import getpass

from dotenv import load_dotenv
from repositoryminer.file import LabeledFileEncoder
from repositoryminer.repository import RepositoryMiner
from repositoryminer.report import create_report

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

    parser = argparse.ArgumentParser(prog='iac-repository-repositoryminer', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + configuration.get('version', '0.0'))

    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_path,
                        help='the local path to the git repository')

    parser.add_argument(action='store',
                        dest='owner',
                        type=str,
                        help='the repository owner')

    parser.add_argument(action='store',
                        dest='name',
                        type=str,
                        help='the repository name')

    parser.add_argument(action='store',
                        dest='dest',
                        type=valid_path,
                        help='destination folder for the reports')

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

    repository_miner = RepositoryMiner(access_token=token,
                                       path_to_repo=args.path_to_repo,
                                       branch=args.branch,
                                       repo_owner=args.owner,
                                       repo_name=args.name)

    if args.verbose:
        print(f'Collecting failure-prone scripts')

    labeled_files = list()
    for labeled_file in repository_miner.mine(labels=None, regex=None):

        if args.verbose:
            print(f'[{labeled_file.commit}] {labeled_file.filepath}\tfixing-commit: {labeled_file.fixing_commit}')

        # Save repository to collection
        labeled_files.append(copy.deepcopy(labeled_file))

    # Generate html report
    html = create_report(repo_owner=args.owner, repo_name=args.name, labeled_files=labeled_files)
    filename_html = os.path.join(args.dest, 'report.html')
    filename_json = os.path.join(args.dest, 'report.json')

    with io.open(filename_html, "w", encoding="utf-8") as f:
        f.write(html)

    json_files = []
    for file in labeled_files:
        json_files.append(json.dumps(file, cls=LabeledFileEncoder))

    with open(filename_json, "w") as f:
        json.dump(json_files, f)

    if args.verbose:
        print(f'HTML report created at {filename_html}')
        print(f'JSON report created at {filename_json}')

    exit(0)


