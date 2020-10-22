import copy
import io
import json
import os

from argparse import ArgumentParser, ArgumentTypeError, Namespace
from datetime import datetime
from getpass import getpass

from dotenv import load_dotenv
from radonminer.files import FailureProneFileEncoder, FailureProneFileDecoder
from radonminer.metrics.ansible import AnsibleMetricsExtractor
from radonminer.metrics.tosca import ToscaMetricsExtractor
from radonminer.mining.ansible import AnsibleMiner
from radonminer.mining.tosca import ToscaMiner
from radonminer.report import create_report

VERSION = '0.3.0'


def valid_dir(x: str) -> str:
    """
    Check if x is a directory and exists
    :param x: a path
    :return: the path if exists; raise an ArgumentTypeError otherwise
    """
    if not os.path.isdir(x):
        raise ArgumentTypeError('Insert a valid path')

    return x


def valid_file(x: str) -> str:
    """
    Check if x is a file and exists
    :param x: a path
    :return: the path if exists; raise an ArgumentTypeError otherwise
    """
    if not os.path.isfile(x):
        raise ArgumentTypeError('Insert a valid path')

    return x


def set_mine_parser(subparsers):
    parser = subparsers.add_parser('mine', help='Mine fixing- and clean- files')
    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_dir,
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
                        type=valid_dir,
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


def set_extract_metrics_parser(subparsers):
    parser = subparsers.add_parser('extract-metrics', help='Extract metrics from the mined files')

    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_dir,
                        help='the local path to the git repository')

    parser.add_argument(action='store',
                        dest='src',
                        type=valid_file,
                        help='the json report generated from a previous run of \'radon-miner mine\'')

    parser.add_argument(action='store',
                        dest='language',
                        type=str,
                        choices=['ansible', 'tosca'],
                        help='extract metrics for Ansible or Tosca')

    parser.add_argument(action='store',
                        dest='metrics',
                        type=str,
                        choices=['product', 'process', 'delta', 'all'],
                        help='the metrics to extract')

    parser.add_argument(action='store',
                        dest='at',
                        type=str,
                        choices=['release', 'commit'],
                        help='extract metrics at each release or commit')

    parser.add_argument(action='store',
                        dest='dest',
                        type=valid_dir,
                        help='destination folder to save the resulting csv')


def get_parser():
    description = 'A Python library and command-line tool to mine Infrastructure-as-Code based software repositories.'

    parser = ArgumentParser(prog='radon-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    subparsers = parser.add_subparsers(dest='command')

    set_mine_parser(subparsers)
    set_extract_metrics_parser(subparsers)

    return parser


def mine(args: Namespace):
    global token
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
            print(f'[{labeled_file.commit}] {labeled_file.filepath}')

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
        json_files.append(FailureProneFileEncoder().default(file))

    with open(filename_json, "w") as f:
        json.dump(json_files, f)

    if args.verbose:
        print(f'HTML report created at {filename_html}')
        print(f'JSON report created at {filename_json}')

    exit(0)


def extract_metrics(args: Namespace):
    global extractor
    with open(args.src, 'r') as f:
        labeled_files = json.load(f, cls=FailureProneFileDecoder)

    if args.language == 'ansible':
        extractor = AnsibleMetricsExtractor(args.path_to_repo)
    elif args.language == 'tosca':
        extractor = ToscaMetricsExtractor(args.path_to_repo)

    assert extractor
    extractor.extract(labeled_files=labeled_files,
                      process=args.metrics in ('process', 'all'),
                      product=args.metrics in ('product', 'all'),
                      delta=args.metrics in ('delta', 'all'),
                      at=args.at)


def main():
    args = get_parser().parse_args()
    if args.command == 'mine':
        mine(args)
    elif args.command == 'extract-metrics':
        extract_metrics(args)
