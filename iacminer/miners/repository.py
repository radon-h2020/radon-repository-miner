"""
A module for mining repositories.
"""
import github
import os
import re

from datetime import datetime, timedelta
from typing import Dict, Generator, NewType, List, Set

Issue = NewType('Issue', github.Issue)

from iacminer import filters
from iacminer.entities.file import FixingFile, LabeledFile
from iacminer.metrics import metrics as metrics_collector
from pydriller.domain.commit import ModificationType
from pydriller.repository_mining import GitRepository, RepositoryMining

# Constants
BUG_RELATED_LABELS = {'bug', 'Bug', 'bug :bug:', 'Bug - Medium', 'Bug - Low', 'Bug - Critical', 'ansible_bug',
                      'Type: Bug', 'Type: bug', 'Type/Bug', 'type: bug 🐛', 'type:bug', 'type: bug', 'type/bug',
                      'kind/bug', 'kind/bugs', 'bug/bugfix', 'bugfix', 'critical-bug', '01 type: bug', 'bug_report',
                      'minor-bug'}


class RepositoryMiner:
    """
    This class is responsible for mining the history of a repository to collect defect-prone and defect-free blueprints.
    """

    def __init__(self, token, path_to_repo: str, branch: str = 'master', owner: str=None, repo: str=None):
        """
        Initialize a new miner for a software repository.

        :param path_to_repo: the path to the repository to analyze;
        :param branch: the branch to analyze. Default 'master';
        :param owner: the repository's owner;
        :param repo: the name of the repository; 
        """

        self.__github = github.Github(token)
        self.path_to_repo = path_to_repo
        self.branch = branch

        self.owner_repo = '/'.join(self.path_to_repo.split('/')[-2:])

        if owner and repo:
            self.owner_repo = '/'.join([owner, repo])

        self.fixing_commits = set()
        self.commit_hashes = [c.hash for c in
                              RepositoryMining(self.path_to_repo, only_in_branch=self.branch).traverse_commits()]

        self.release_hashes = [c.hash for c in
                               RepositoryMining(self.path_to_repo, only_releases=True).traverse_commits()]

    @staticmethod
    def get_file_content(path) -> str:
        """
        Return the content of a file
        :param path: the path to the file
        :return: the content of the file, if exists; None, otherwise.
        """
        if not os.path.isfile(path):
            return None

        with open(path, 'r') as f:
            return f.read()

    def get_files(self) -> Set[str]:
        """
        Return all the files in the repository
        :return: a set of strings representing the path of the files in the repository
        """

        files = set()

        for root, _, filenames in os.walk(self.path_to_repo):
            if '.git' in root:
                continue
            for filename in filenames:
                path = os.path.join(root, filename)
                path = path.replace(self.path_to_repo, '')
                if path.startswith('/'):
                    path = path[1:]

                files.add(path)

        return files

    def get_labels(self) -> Set[str]:
        """
        Returns all the issue labels in a repositories
        :return: a set of distinct labels
        """

        repo = self.__github.get_repo(self.owner_repo)
        labels = set()
        for label in repo.get_labels():
            if type(label) == github.Label.Label:
                labels.add(label.name)

        return labels

    def get_closed_issues(self, label: str) -> List[Issue]:
        """
        Get all the closed issues with a given label

        :param label: the label of the issue (e.g., 'bug')
        :return: yield the closed issues with that label
        """
        
        repo = self.__github.get_repo(self.owner_repo)
        label = repo.get_label(label)
        issues = list()
        for issue in repo.get_issues(state='closed', labels=[label], sort='created', direction='desc'):
            issues.append(issue)

        return issues

    def get_issue_labels(self, num: int) -> Set[str]:
        """
        Return the labels of the issue number 'num'

        :param num: the issue number
        :return: the issue labels
        """

        repo = self.__github.get_repo(self.owner_repo)
        labels = set()

        try:
            issue = repo.get_issue(num)

            if issue.state == 'closed':
                for label in issue.labels:
                    labels.add(str(label))
        except Exception as e:
            print(str(e))

        return labels

    def get_fixing_commits_from_closed_issues(self) -> Set[str]:
        """
        Collect fixing-commit hashes by analyzing the closed issues
        :return: the set of fixing-commit hashes
        """
        labels = self.get_labels()  # Collect all the labels from the repository
        labels = BUG_RELATED_LABELS.intersection(labels)  # Keep only labels related to defects

        fixing_commit_hashes = set()

        for label in labels:
            for issue in self.get_closed_issues(label):
                for e in issue.get_events():
                    is_merged = e.event.lower() == 'merged'
                    is_closed = e.event.lower() == 'closed'

                    if (is_merged or is_closed) and e.commit_id:
                        fixing_commit_hashes.add(e.commit_id)

        return fixing_commit_hashes

    def get_fixing_commits_from_commit_messages(self) -> Set[str]:
        """
        Collect fixing-commit hashes by analyzing the commit messages
        :return: the set of fixing-commit hashes
        """

        fixing_commit_hashes = set()

        for commit in RepositoryMining(self.path_to_repo, only_in_branch=self.branch).traverse_commits():

            # Remove words ending with 'bug' or 'fix' (e.g., 'debug' and 'prefix') from the commit message
            p = re.compile(r'(\w+(bug|fix)\w)*', re.IGNORECASE)
            msg = commit.msg
            match = p.match(msg)
            if match:
                msg = re.sub(match.group(), '', msg)

            # Match the regular expression to the messge
            if re.match(r'(bug|fix|error|issue|crash|problem|fail|defect|patch)', msg.lower()):
                fixing_commit_hashes.add(commit.hash)

        return fixing_commit_hashes

    def set_fixing_commits(self) -> None:
        """
        Set commits that have fixed closed bug-related issues
        :return: None
        """
        from_issues = self.get_fixing_commits_from_closed_issues()
        from_commit = self.get_fixing_commits_from_commit_messages()
        self.fixing_commits = from_issues.union(from_commit)

    def get_fixing_files(self) -> List:
        """
        Collect and filter the files involved in a fixing commit
        :return: the set of files that fixed a bug
        """

        if not self.fixing_commits:
            return list()

        # Sort fixing commits in chronological order
        sorted_fixing_commits = [sha for sha in self.commit_hashes if sha in list(self.fixing_commits)]
        first_fix, last_fix = sorted_fixing_commits[0], sorted_fixing_commits[-1]

        fixing_files = list()
        renamed_files = dict()
        git_repo = GitRepository(self.path_to_repo)

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=last_fix,
                                       to_commit=first_fix,
                                       order='reverse',
                                       only_in_branch=self.branch).traverse_commits():

            # Discard commits that do not modify at least one Ansible file
            if not any(filters.is_ansible_file(modified_file.new_path) for modified_file in commit.modifications):
                if commit.hash in self.fixing_commits:
                    self.fixing_commits.remove(commit.hash)
                continue

            # Find buggy inducing commits
            for modified_file in commit.modifications:

                # Not interested in ADDED and DELETED files
                if modified_file.change_type not in (ModificationType.MODIFY, ModificationType.RENAME):
                    continue

                # If renamed then handle renaming
                if modified_file.change_type == ModificationType.RENAME:

                    if modified_file.new_path in renamed_files:
                        renamed_files[modified_file.old_path] = renamed_files[modified_file.new_path]

                    elif commit.hash in self.fixing_commits:
                        renamed_files[modified_file.old_path] = modified_file.new_path

                # Else
                if commit.hash not in self.fixing_commits:
                    continue

                # Not interested in files other than Ansible
                if not filters.is_ansible_file(modified_file.new_path):
                    continue

                # Identify bug-inducing commits
                bug_inducing_commits = git_repo.get_commits_last_modified_lines(commit, modified_file)

                if not bug_inducing_commits:
                    continue

                fix = FixingFile(filepath=renamed_files.get(modified_file.new_path, modified_file.new_path),
                                 bics=bug_inducing_commits[modified_file.new_path],
                                 fic=commit.hash)

                if fix in fixing_files:
                    # Update existing fixing file
                    idx = fixing_files.index(fix)

                    # If all BICs of the latest fixing commit are older than the current fixing commit then the current
                    # fix makes the file 'clean' and is added as a separate file; otherwise the new bics are added to
                    # the file
                    if all(self.commit_hashes.index(bic) > self.commit_hashes.index(fix.fic) for bic in
                           fixing_files[idx].bics):
                        fixing_files.append(fix)
                    else:
                        fixing_files[idx].bics.update(bug_inducing_commits[modified_file.new_path])
                else:
                    fixing_files.append(fix)

        return fixing_files

    def label(self, files: List[FixingFile]) -> List[LabeledFile]:
        """
        Start labeling process
        :param files: a list of FixingFile objects
        :return: a list of labeled files
        """

        if not files:
            return list()

        files = files.copy()
        under_labeling = dict()
        labeled_files = list()

        for commit in RepositoryMining(self.path_to_repo, order='reverse').traverse_commits():

            for i in range(len(list(files)) - 1, -1, -1):
                fix = files[i]

                if fix.fic == commit.hash:
                    under_labeling[fix.fic] = fix
                    del files[i]

            finished = set()

            for fic_hash, fix in under_labeling.items():

                if not fix.bics:
                    finished.add(fic_hash)
                    continue

                if commit.hash in fix.bics:
                    fix.bics.remove(commit.hash)

                if fix.filepath and commit.hash != fic_hash:
                    labeled_files.append(
                        LabeledFile(filepath=fix.filepath,
                                    commit=commit.hash,
                                    label=LabeledFile.Label.DEFECT_PRONE,
                                    fixing_commit=fix.fic))

                # Handle file renaming
                for modified_file in commit.modifications:

                    if not fix.filepath:
                        continue

                    if fix.filepath not in (modified_file.old_path, modified_file.new_path):
                        continue

                    if modified_file.change_type == ModificationType.ADD:
                        fix.filepath = None

                    fix.filepath = modified_file.old_path

            for hash in finished:
                del under_labeling[hash]

        return labeled_files

    def mine(self) -> Generator[Dict, None, None]:
        """
        Mine the repositories
        :return: a list of LabeledFile objects
        """

        self.set_fixing_commits()
        labeled_files = self.label(self.get_fixing_files())

        git_repo = GitRepository(self.path_to_repo)

        # Group labeled files per commit
        commit_file_map = dict()
        for file in labeled_files:
            commit_file_map.setdefault(file.commit, list()).append(file)

        last_release_date = None
        iac_metrics_before = dict()  # Values for iac metrics in the last release
        path_when_added = dict()

        for commit in RepositoryMining(self.path_to_repo).traverse_commits():

            # To handle renaming in iac_metrics_before
            for modified_file in commit.modifications:

                old_path = modified_file.old_path
                new_path = modified_file.new_path

                if old_path in path_when_added:
                    path_when_added[new_path] = path_when_added.pop(old_path)
                else:
                    path_when_added[new_path] = new_path

                if old_path != new_path and old_path in iac_metrics_before:
                    # Rename key old_path wit new_path
                    iac_metrics_before[new_path] = iac_metrics_before.pop(old_path)

            if not last_release_date:
                last_release_date = commit.committer_date

            if commit.hash not in self.release_hashes:
                continue

            # PROCESS metrics
            process_metrics = metrics_collector.process_metrics(self.path_to_repo,
                                                                since=last_release_date + timedelta(minutes=1),
                                                                to=commit.committer_date)
            last_release_date = commit.committer_date

            # Checkout to commit to extract product metrics from each file
            git_repo.checkout(commit.hash)

            # IAC metrics
            all_filepaths = self.get_files()
            labeled_this_commit = commit_file_map.get(commit.hash, [])

            defect_prone = all_filepaths.intersection(
                [file.filepath for file in labeled_this_commit if file.label == LabeledFile.Label.DEFECT_PRONE])
            defect_free = all_filepaths - defect_prone

            if not defect_prone:  # Keep only releases having at least one defect files.
                continue

            for filepath in defect_free.union(defect_prone):

                if not filters.is_ansible_file(filepath):
                    continue

                # Product metrics
                content = self.get_file_content(os.path.join(self.path_to_repo, filepath))

                try:
                    iac_metrics = metrics_collector.product_metrics(content)
                except (TypeError, ValueError):
                    # Not a valid YAML or empty content
                    label = "defect-prone" if filepath in defect_prone else "defect-free"
                    print(f'>>> Commit: {commit.hash} - Cannot properly {filepath} - The file label is {label}.')
                    continue

                # Tokens
                tokens = metrics_collector.text_metrics(content)

                # Delta metrics
                delta_metrics = dict()

                previous = iac_metrics_before.get(filepath, dict())
                for k, v in previous.items():
                    v_delta = iac_metrics.get(k, 0) - v
                    delta_metrics[f'delta_{k}'] = round(v_delta, 3)

                iac_metrics_before[filepath] = iac_metrics.copy()

                metrics = iac_metrics
                metrics.update(delta_metrics)

                # Getting process metrics for the specific file
                metrics['change_set_max'] = process_metrics[0]
                metrics['change_set_avg'] = process_metrics[1]
                metrics['code_churn'] = process_metrics[2].get(filepath, 0)
                metrics['code_churn_max'] = process_metrics[3].get(filepath, 0)
                metrics['code_churn_avg'] = process_metrics[4].get(filepath, 0)
                metrics['commits_count'] = process_metrics[5].get(filepath, 0)
                metrics['contributors'] = process_metrics[6].get(filepath, 0)
                metrics['minor_contributors'] = process_metrics[7].get(filepath, 0)
                metrics['highest_experience'] = process_metrics[8].get(filepath, 0)
                metrics['median_hunks_count'] = process_metrics[9].get(filepath, 0)
                metrics['loc_added'] = process_metrics[10].get(filepath, 0)
                metrics['loc_added_max'] = process_metrics[11].get(filepath, 0)
                metrics['loc_added_avg'] = process_metrics[12].get(filepath, 0)
                metrics['loc_removed'] = process_metrics[13].get(filepath, 0)
                metrics['loc_removed_max'] = process_metrics[14].get(filepath, 0)
                metrics['loc_removed_avg'] = process_metrics[15].get(filepath, 0)

                metrics.update(
                    dict(commit=commit.hash,  # release commit
                         committed_at=datetime.timestamp(commit.committer_date),  # release date
                         defective=1 if filepath in defect_prone else 0,
                         filepath=filepath,
                         repo='/'.join(self.path_to_repo.split('/')[-2:]),  # e.g., 'tmp/owner/repo -> owner/repo,
                         path_when_added=path_when_added.get(filepath, 'NA'),
                         tokens=' '.join(tokens))
                )

                yield metrics

            git_repo.reset()  # Reset repository's status
