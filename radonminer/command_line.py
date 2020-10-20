import argparse
import copy
import io
import json
import os

from datetime import datetime
from getpass import getpass

from dotenv import load_dotenv
from radonminer.file import LabeledFileEncoder
from radonminer.mining.ansible import AnsibleMiner
from radonminer.mining.tosca import ToscaMiner
from radonminer.report import create_report

VERSION = '0.3.0'


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
    description = 'A Python library and command-line tool to mine Infrastructure-as-Code based software repositories.'

    parser = argparse.ArgumentParser(prog='radon-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)

    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_path,
                        help='the local path to the git repository')

    parser.add_argument(action='store',
                        dest='host',
                        type=str,
                        choices=['github', 'gitlab'],
                        help='the source code versioning host')

    parser.add_argument(action='store',
                        dest='language',
                        type=str,
                        choices=['ansible', 'tosca'],
                        help='mine only commits modifying files of this language')

    parser.add_argument(action='store',
                        dest='full_name_or_id',
                        type=str,
                        help='the repository full name or id (e.g., radon-h2020/radon-repository-miner')

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
    global token
    args = get_parser().parse_args()

    load_dotenv()

    if args.host == 'github':
        token = os.getenv('GITHUB_ACCESS_TOKEN')
    elif args.host == 'gitlab':
        token = os.getenv('GITLAB_ACCESS_TOKEN')

    if token is None:
        token = getpass('Access token:')

    if args.verbose:
        print(f'Mining: {args.path_to_repo} [{datetime.now().hour}:{datetime.now().minute}]')

    if args.language == 'ansible':
        miner = AnsibleMiner(access_token=token,
                             path_to_repo=args.path_to_repo,
                             branch=args.branch,
                             host=args.host,
                             full_name_or_id=args.full_name_or_id)
    else:
        miner = ToscaMiner(access_token=token,
                           path_to_repo=args.path_to_repo,
                           branch=args.branch,
                           host=args.host,
                           full_name_or_id=args.full_name_or_id)

    if args.verbose:
        print(f'Collecting failure-prone scripts')

    labeled_files = list()
    for labeled_file in miner.mine(labels=None, regex=None):

        if args.verbose:
            print(f'[{labeled_file.commit}] {labeled_file.filepath}\tfixing-commit: {labeled_file.fixing_commit}')

        # Save repository to collection
        labeled_files.append(copy.deepcopy(labeled_file))

    # Generate html report
    html = create_report(full_name_or_id=args.full_name_or_id, labeled_files=labeled_files)
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
