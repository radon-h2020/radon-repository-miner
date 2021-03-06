import copy
import io
import json
import os

from argparse import ArgumentParser, ArgumentTypeError, Namespace
from datetime import datetime

from repominer.files import FixedFileEncoder, FixedFileDecoder, FailureProneFileEncoder, FailureProneFileDecoder
from repominer.metrics.ansible import AnsibleMetricsExtractor
from repominer.metrics.tosca import ToscaMetricsExtractor
from repominer.mining.ansible import AnsibleMiner
from repominer.mining.tosca import ToscaMiner

VERSION = '0.9.6'


def valid_dir_or_url(x: str) -> str:
    """
    Check if x is a directory and exists, or a remote url
    :param x: a path
    :return: the path if exists or is a remote url; raise an ArgumentTypeError otherwise
    """
    if not (os.path.isdir(x) or x.startswith("git@") or x.startswith("https://")):
        raise ArgumentTypeError('Insert a valid path or url')

    return x


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
                        dest='info_to_mine',
                        type=str,
                        choices=['fixing-commits', 'fixed-files', 'failure-prone-files'],
                        help='the information to mine')

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
                        dest='repository',
                        help='the repository full name: <owner/name> (e.g., radon-h2020/radon-repository-miner)')

    parser.add_argument(action='store',
                        dest='dest',
                        type=valid_dir,
                        help='destination folder for the reports')

    parser.add_argument('-b', '--branch',
                        action='store',
                        dest='branch',
                        type=str,
                        default='master',
                        help='the repository branch to mine (default: %(default)s)')

    parser.add_argument('--exclude-commits',
                        action='store',
                        dest='exclude_commits',
                        type=valid_file,
                        help='the path to a JSON file containing the list of commit hashes to exclude')

    parser.add_argument('--include-commits',
                        action='store',
                        dest='include_commits',
                        type=valid_file,
                        help='the path to a JSON file containing the list of commit hashes to include')

    parser.add_argument('--exclude-files',
                        action='store',
                        dest='exclude_files',
                        type=valid_file,
                        help='the path to a JSON file containing the list of FixedFiles to exclude')

    parser.add_argument('--verbose',
                        action='store_true',
                        dest='verbose',
                        default=False,
                        help='show log')


def set_extract_metrics_parser(subparsers):
    parser = subparsers.add_parser('extract-metrics', help='Extract metrics from the mined files')

    parser.add_argument(action='store',
                        dest='path_to_repo',
                        type=valid_dir_or_url,
                        help='the absolute path to a cloned repository or the url to a remote repository')

    parser.add_argument(action='store',
                        dest='src',
                        type=valid_file,
                        help='the path to report.json generated by a previous run of \'repo-miner mine\'')

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

    parser.add_argument('--verbose',
                        action='store_true',
                        dest='verbose',
                        default=False,
                        help='show log')


def get_parser():
    description = 'A Python library and command-line tool to mine Infrastructure-as-Code based software repositories.'

    parser = ArgumentParser(prog='repo-miner', description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    subparsers = parser.add_subparsers(dest='command')

    set_mine_parser(subparsers)
    set_extract_metrics_parser(subparsers)

    return parser


class MinerCLI:

    def __init__(self, args: Namespace):
        self.args = args

        if not hasattr(args, 'host') or args.host not in ('github', 'gitlab'):
            print('Please, select github or gitlab')
            exit(1)
        elif args.host == 'github':
            url_to_repo = f'https://github.com/{args.repository}'
        elif args.host == 'gitlab':
            url_to_repo = f'https://gitlab.com/{args.repository}'

        if not hasattr(args, 'language') or args.language not in ('ansible', 'tosca'):
            print('Please, select ansible or tosca')
            exit(2)
        elif args.language == 'ansible':
            self.miner = AnsibleMiner(url_to_repo=url_to_repo, branch=args.branch if hasattr(args, 'branch') else None)
        elif args.language == 'tosca':
            self.miner = ToscaMiner(url_to_repo=url_to_repo, branch=args.branch if hasattr(args, 'branch') else None)

    def mine(self):

        if self.args.verbose:
            print(f'Mining {self.args.repository} [started at: {datetime.now().hour}:{datetime.now().minute}]')

        self.mine_fixing_commits()

        if self.args.info_to_mine in ('fixed-files', 'failure-prone-files'):
            self.mine_fixed_files()

        if self.args.info_to_mine == 'failure-prone-files':
            self.mine_failure_prone_files()

        exit(0)

    def mine_fixing_commits(self):

        if hasattr(self.args, 'exclude_commits') and self.args.exclude_commits:
            with open(self.args.exclude_commits, 'r') as f:
                commits = json.load(f)
                self.miner.exclude_commits = set(commits)

        if hasattr(self.args, 'include_commits') and self.args.include_commits:
            with open(self.args.include_commits, 'r') as f:
                commits = json.load(f)
                self.miner.fixing_commits = commits

        if self.args.verbose:
            print('Identifying fixing-commits')

        fixing_commits = self.miner.get_fixing_commits()

        if self.args.verbose:
            print(f'Saving {len(fixing_commits)} fixing-commits [{datetime.now().hour}:{datetime.now().minute}]')

        filename_json = os.path.join(self.args.dest, 'fixing-commits.json')

        with io.open(filename_json, "w") as f:
            json.dump(fixing_commits, f)

        if self.args.verbose:
            print(f'JSON created at {filename_json}')

    def mine_fixed_files(self):

        if hasattr(self.args, 'exclude_files') and self.args.exclude_files:
            with open(self.args.exclude_files, 'r') as f:
                files = json.load(f, cls=FixedFileDecoder)
                self.miner.exclude_fixed_files = files

        if self.args.verbose:
            print(f'Identifying {self.args.language} files modified in fixing-commits')

        fixed_files = self.miner.get_fixed_files()

        if self.args.verbose:
            print(f'Saving {len(fixed_files)} fixed-files [{datetime.now().hour}:{datetime.now().minute}]')

        filename_json = os.path.join(self.args.dest, 'fixed-files.json')
        json_files = []
        for file in fixed_files:
            json_files.append(FixedFileEncoder().default(file))

        with io.open(filename_json, "w") as f:
            json.dump(json_files, f)

        if self.args.verbose:
            print(f'JSON created at {filename_json}')

    def mine_failure_prone_files(self):
        if self.args.verbose:
            print('Identifying and labeling failure-prone files')

        failure_prone_files = [copy.deepcopy(file) for file in self.miner.label()]

        if self.args.verbose:
            print('Saving failure-prone files')

        filename_json = os.path.join(self.args.dest, 'failure-prone-files.json')

        json_files = []
        for file in failure_prone_files:
            json_files.append(FailureProneFileEncoder().default(file))

        with open(filename_json, "w") as f:
            json.dump(json_files, f)

        if self.args.verbose:
            print(f'JSON created at {filename_json}')


def extract_metrics(args: Namespace):
    global extractor

    if args.verbose:
        print(
            f'Extracting metrics from {args.path_to_repo} using report {args.src} [started at: {datetime.now().hour}:{datetime.now().minute}]')

    with open(args.src, 'r') as f:
        labeled_files = json.load(f, cls=FailureProneFileDecoder)

    if args.verbose:
        print(f'Setting up {args.language} metrics extractor')

    if args.language == 'ansible':
        extractor = AnsibleMetricsExtractor(args.path_to_repo, at=args.at)
    elif args.language == 'tosca':
        extractor = ToscaMetricsExtractor(args.path_to_repo, at=args.at)

    if args.verbose:
        print(f'Extracting {args.metrics} metrics')

    assert extractor
    extractor.extract(labeled_files=labeled_files,
                      process=args.metrics in ('process', 'all'),
                      product=args.metrics in ('product', 'all'),
                      delta=args.metrics in ('delta', 'all'))

    extractor.to_csv(os.path.join(args.dest, 'metrics.csv'))

    if args.verbose:
        print(f'Metrics saved at {args.dest}/metrics.csv [completed at: {datetime.now().hour}:{datetime.now().minute}]')


def main():
    args = get_parser().parse_args()
    if args.command == 'mine':
        MinerCLI(args).mine()
    elif args.command == 'extract-metrics':
        extract_metrics(args)
