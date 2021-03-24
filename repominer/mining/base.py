import os
import nltk
import re

from deprecated import deprecated
from typing import Dict, Generator, List, Set

from pydriller.domain.commit import Commit, ModificationType
from pydriller.repository_mining import GitRepository, RepositoryMining

from repominer import utils
from repominer.files import FixedFile, FailureProneFile
from repominer.mining import rules

# Important: downloading resources for NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Constants
BUG_RELATED_LABELS = {'bug', 'Bug', 'bug :bug:', 'Bug - Medium', 'Bug - Low', 'Bug - Critical', 'ansible_bug',
                      'Type: Bug', 'Type: bug', 'Type/Bug', 'type: bug 🐛', 'type:bug', 'type: bug', 'type/bug',
                      'kind/bug', 'kind/bugs', 'bug/bugfix', 'bugfix', 'critical-bug', '01 type: bug', 'bug_report',
                      'minor-bug'}

FIXING_COMMITS_REGEX = r'(bug|fix|error|crash|problem|fail|defect|patch)'

full_name_pattern = re.compile(r'(github|gitlab){1}\.com/([\w\W]+)$')


class BaseMiner:
    """
    This is the base class to miner a software repositories.

    It allows for mining bug-fixing commits, fixed files, and bug-introducing commits.
    It can be extended to instantiate the miner in the context of specific languages (e.g., Ansible and Tosca).
    """

    def __init__(self,
                 url_to_repo: str,
                 branch: str = 'master'):
        """
        The class constructor.
        Initialize a new BaseMiner.

        Parameters
        ----------
        url_to_repo : str
            the url to a remote Github or Gitlab repository

        branch : str
            the branch to analyze. Default 'master'


        Attributes
        ----------
        repository : str
            Repository full name (e.g., radon-h2020/radon-repository-miner).
            The value is automatically extracted from parameter ``url_to_repo``.

        branch : str
            Repository's branch to analyze.

        commit_hashes : List[str]
            List of commit hash on the repository's branch, ordered by creation date.

        exclude_commits : Set[str]
            Set of commit hash to exclude from mining.

            Mining bug-fixing commits might lead several false positives, i.e., commits that do not actually fix bugs.
            If you are certain that some commits do not fix bugs, before mining, you can specify their hash as follows:

            Example
            -------
            .. highlight:: python
            .. code-block:: python

                from repominer.mining.base import BaseMiner

                miner = BaseMiner('https://github.com/radon-h2020/radon-repository-miner')
                miner.exclude_commits = {'521515108c4fee9a4bd1147fc42936768297e3b6'}

        exclude_fixed_files : List[str]
            Set of fixed files to exclude from mining.
            Fixed files are files modified in a bug-fixing commit.

            When fixing a bug, several files might be modified but not all of them contributed to fix the bug.
            For example, someone could fix a bug in a file, and at the same time modify another file not involved
            in the fix, such as a README.md.

            If you are certain that some files in a give commit are not involved in fixing bugs, you can tell the miner
            to ignore them as follow:

            Example
            -------
            .. highlight:: python
            .. code-block:: python

                from repominer.files import FixedFile
                from repominer.mining.base import BaseMiner

                miner = BaseMiner('https://github.com/radon-h2020/radon-repository-miner')
                miner.exclude_fixed_files = [
                    FixedFile(filepath='CHANGELOG.md',
                              fic='f350e05696db1c5f78320483e0e44e7aea410449',
                              bic=None),
                    FixedFile(filepath='repominer/cli.py',
                              fic='f350e05696db1c5f78320483e0e44e7aea410449',
                              bic=None)
                ]

        fixing_commits : List[str]
            List of bug-fixing commit hashes.

            Bug-fixings commits are identified by the methods ``get_fixing_commits_from_closed_issues`` and
            ``get_fixing_commits_from_commit_messages``.

            Although, if you are certain that some commits fix bugs, e.g., because of a previous manual analysis,
            you can specify them in advance to speed up the mining as follows:

            Example
            -------
            .. highlight:: python
            .. code-block:: python

                from repominer.mining.base import BaseMiner

                miner = BaseMiner('https://github.com/radon-h2020/radon-repository-miner')
                miner.fixing_commits = ['f350e05696db1c5f78320483e0e44e7aea410449']

            This is useful when you have to run the miner again on future commits, and you already have results from the
            past runs.

        fixed_files : List[FixedFile]
            List of FixedFiles objects.
            Fixed files are files modified in bug-fixing commits.

            They are identified by the method ``get_fixed_files``.
            Unlike ``fixing_commits``, it cannot be used to inlude fixed file, as it resets at every ``get_fixed_files``
            call.
            This is due to the algorithm used to identify them.

        """

        match = full_name_pattern.search(url_to_repo.replace('.git', ''))
        self.repository = match.groups()[1]
        self.branch = branch

        self.exclude_commits = set()  # This is to set up commits known to be non-fixing in advance
        self.exclude_fixed_files = list()  # This is to set up files in fixing-commits known to be false-positive
        self.fixing_commits = list()
        self.fixed_files = list()

        self.path_to_repo = os.path.join(os.getenv('TMP_REPOSITORIES_DIR'), self.repository.split('/')[1])

        # Get all the repository commits sorted by commit date
        self.commit_hashes = [c.hash for c in
                              RepositoryMining(
                                  path_to_repo=self.path_to_repo if os.path.isdir(self.path_to_repo) else url_to_repo,
                                  clone_repo_to=os.getenv('TMP_REPOSITORIES_DIR'),
                                  only_in_branch=self.branch,
                                  order='date-order').traverse_commits()]

        self.FixingCommitClassifier = FixingCommitClassifier

    def discard_undesired_fixing_commits(self, commits: List[str]) -> None:
        """
        Discard undesired commits.

        Given a list of commit hash, this method discard those that are deemed undesired.
        Undesired commits depends on the problem being formulated. For example, if the user is mining fixing-commits for
        Ansible, an undesired commit might be one modifying not-Ansible files.

        Note, the update occurs in-place. That is, the original list is updated.

        Parameters
        ----------
        commits : List[str]
            List of commit hash

        """
        pass

    def get_fixing_commits(self) -> Dict[str, List[str]]:
        """
        Return a list of bug-fixing commit hash, categorized as fixing "conditionals", "configuration data",
        "dependencies", "documentation", "idempotency", "security", "service", "syntax".

        This method returns the commits whose message indicates defective scripts.
        `Note:` Beside returning the list of bug-fixing commits, it also updates the attribute ``fixing_commits``.

        Returns
        -------
        List[str]
            A dictionary of bug-fixing commits hashes and boolean values for every fixing labels.
            {'hash1': {
                   'SERVICE': true/false,
                   'SYNTAX': true/false,
                   ...
                }
                ...
            }
        """

        commits_labels = {}
        commits = []

        for commit in RepositoryMining(self.path_to_repo, only_in_branch=self.branch).traverse_commits():

            if (commit.hash in self.exclude_commits) or (commit.hash in self.fixing_commits):
                continue

            fcc = self.FixingCommitClassifier(commit)

            if fcc.fixes_dependency():
                commits_labels.setdefault(commit.hash, []).append('DEPENDENCY')
            if fcc.fixes_documentation():
                commits_labels.setdefault(commit.hash, []).append('DOCUMENTATION')
            if fcc.fixes_syntax():
                commits_labels.setdefault(commit.hash, []).append('SYNTAX')
            if fcc.fixes_service():
                commits_labels.setdefault(commit.hash, []).append('SERVICE')
            if fcc.fixes_security():
                commits_labels.setdefault(commit.hash, []).append('SECURITY')
            if fcc.fixes_conditional():
                commits_labels.setdefault(commit.hash, []).append('CONDITIONAL')
            if fcc.fixes_configuration_data():
                commits_labels.setdefault(commit.hash, []).append('CONFIGURATION_DATA')
            if fcc.fixes_idempotency():
                commits_labels.setdefault(commit.hash, []).append('IDEMPOTENCY')
            if commit.hash in commits_labels:
                commits.append(commit.hash)

        if commits:
            # Discard commits that do not touch IaC files
            self.discard_undesired_fixing_commits(commits)

            # Update the list of fixing commits
            self.fixing_commits.extend(commits)

            # Sort fixing_commits in ascending order of date
            self.sort_commits(self.fixing_commits)

            for sha, _ in list(commits_labels.items()):
                if sha not in commits:  # It means it was an undesired commit
                    del commits_labels[sha]

        return commits_labels

    def get_fixed_files(self) -> List[FixedFile]:
        """
        Return a list of FixedFile objects.

        A FixeFile is a file modified in a bug-fixing commit that consists of a filename, hash of the commit that fixed
        it, and hash of the commit that introduced the bug.

        It uses the SZZ algorithm implemented in PyDriller to identify the oldest commit that introduced the bug,
        referred to as bug-introducing commit.

        `Note:` before calling this method, it is necessary that you run at least one between
        `get_fixing_commits_from_closed_issues` and `get_fixing_commits_from_commit_messages`.


        Returns
        -------
        List[FixedFile]
            List of FixedFile objects

        """

        if not self.fixing_commits:
            return list()

        self.sort_commits(self.fixing_commits)

        self.fixed_files = list()
        renamed_files = dict()
        git_repo = GitRepository(self.path_to_repo)

        if len(self.fixing_commits) == 1:
            repository_mining = RepositoryMining(self.path_to_repo,
                                                 single=self.fixing_commits[0],
                                                 only_in_branch=self.branch)
        else:
            repository_mining = RepositoryMining(self.path_to_repo,
                                                 from_commit=self.fixing_commits[-1],  # Last fixing-commit by date
                                                 to_commit=self.fixing_commits[0],  # First fixing-commit by date
                                                 order='reverse',
                                                 only_in_branch=self.branch)

        # Traverse commits from the latest to the first fixing-commit
        for commit in repository_mining.traverse_commits():

            for modified_file in commit.modifications:

                # Not interested in ADDED and DELETED files
                if modified_file.change_type not in (ModificationType.MODIFY, ModificationType.RENAME):
                    continue

                # If RENAMED then handle renaming
                if modified_file.change_type == ModificationType.RENAME:

                    if modified_file.new_path in renamed_files:
                        renamed_files[modified_file.old_path] = renamed_files[modified_file.new_path]

                    elif commit.hash in self.fixing_commits:
                        renamed_files[modified_file.old_path] = modified_file.new_path

                # This is to ensure that renamed files are tracked. Then, if the commit is not a fixing-commit then
                # go to the next (previous commit in chronological order)
                if commit.hash not in self.fixing_commits:
                    continue

                # Not interested in type of files
                if self.ignore_file(modified_file.new_path, modified_file.source_code):
                    continue

                if any(file.filepath == modified_file.new_path and file.fic == commit.hash for file in
                       self.exclude_fixed_files):
                    continue

                # Identify bug-inducing commits. Dict[modified_file, Set[commit_hashes]]
                bug_inducing_commits = git_repo.get_commits_last_modified_lines(commit, modified_file)

                if not bug_inducing_commits.get(modified_file.new_path):
                    continue
                else:
                    bug_inducing_commits = list(bug_inducing_commits[modified_file.new_path])
                    self.sort_commits(bug_inducing_commits)
                    bic = bug_inducing_commits[0]  # bic is the oldest bug-inducing-commit

                current_fix = FixedFile(filepath=renamed_files.get(modified_file.new_path, modified_file.new_path),
                                        bic=bic,
                                        fic=commit.hash)

                if current_fix not in self.fixed_files:
                    self.fixed_files.append(current_fix)
                else:
                    idx = self.fixed_files.index(current_fix)
                    existing_fix = self.fixed_files[idx]

                    # If the current FIC is older than the existing bic, then save it as a new FixedFile.
                    # Else it means the current fix is between the existing fix bic and fic.
                    # If the current BIC is older than the existing bic, then update the bic.
                    if self.commit_hashes.index(current_fix.fic) < self.commit_hashes.index(existing_fix.bic):
                        self.fixed_files.append(current_fix)
                    elif self.commit_hashes.index(current_fix.bic) < self.commit_hashes.index(existing_fix.bic):
                        existing_fix.bic = current_fix.bic

        return self.fixed_files.copy()

    def ignore_file(self, path_to_file: str, content: str = None) -> bool:
        """
        Ignore a file.

        When looking for fixed files in ``get_fixed_files``, you might want to consider only files with some characteristics,
        and ignore all the others.
        For example, when instantiating an ``ToscaMiner``, this method ignore all the non-Ansible files, based on their
        filepath and content. That is, only files terminating with .yml, .yaml, or .tosca, or which content contains the
        keyword ``tosca_definitions_version`` are kept.

        Parameters
        ----------
        path_to_file: str
            The filepath (e.g., repominer/mining/base.py).

        content: str
            The file content.

        Returns
        -------
        bool
            True if the file must be ignore. False, otherwise.

        """
        return False

    def label(self) -> Generator[FailureProneFile, None, None]:
        """
        For each FixedFile object, yield a FailureProneFile object for each commit between the FixedFile's
        bug-introducing-commit and its fixing-commit.

        `Note:` make sure to run the method ``get_fixed_files`` before.

        Yields
        ------
        FailureProneFile
            A FailureProneFile object.

        """

        if not (self.fixing_commits or self.fixed_files):
            return

        labeling = dict()
        for file in self.fixed_files:
            labeling.setdefault(file.filepath, list()).append(file)

        for commit in RepositoryMining(self.path_to_repo,
                                       from_commit=self.fixing_commits[-1],
                                       to_commit=self.commit_hashes[0],
                                       order='reverse').traverse_commits():

            for files in labeling.values():
                for file in files:

                    idx_fic = self.commit_hashes.index(file.fic)
                    idx_bic = self.commit_hashes.index(file.bic)
                    idx_commit = self.commit_hashes.index(commit.hash)

                    if idx_fic > idx_commit >= idx_bic:
                        yield FailureProneFile(filepath=file.filepath,
                                               commit=commit.hash,
                                               fixing_commit=file.fic)

                    if idx_commit == idx_bic and file.filepath in labeling:
                        if file in labeling[file.filepath]:
                            labeling[file.filepath].remove(file)

            # Handle file renaming
            for modified_file in commit.modifications:
                filepath = modified_file.new_path

                for file in list(labeling.get(filepath, list())):
                    if self.commit_hashes.index(file.fic) > self.commit_hashes.index(
                            commit.hash) >= self.commit_hashes.index(file.bic):

                        if modified_file.change_type == ModificationType.ADD:
                            if filepath in labeling and file in labeling[filepath]:
                                labeling[filepath].remove(file)
                        elif modified_file.change_type == ModificationType.RENAME:
                            file.filepath = modified_file.old_path
                        break

    def sort_commits(self, commits: List[str]) -> None:
        """
        Sort a list of commits in chronological order.

        Parameters
        ----------
        commits : List[str]
            List of commits hash to sort.

        """
        sorted_commits = [sha for sha in self.commit_hashes if sha in commits]
        commits.clear()
        commits.extend(sorted_commits)


class FixingCommitClassifier:
    """
    This class implements rules to detect fixing commits categories related to IaC defects, as defined in
    http://chrisparnin.me/pdf/GangOfEight.pdf.
    """

    def __init__(self, commit: Commit):
        """
        The class constructor.

        Parameters
        ----------
        commit: Commit
            The commit to analyze.

        Raises
        ------
        TypeError
            If commit is None

        """

        if commit is None:
            raise TypeError('Expected a pydriller.domain.commit.Commit object, not None.')

        self.commit = commit
        self.sentences = []  # will be list of tokens list

        for sentence in nltk.sent_tokenize(commit.msg):
            # split into words
            tokens = nltk.tokenize.word_tokenize(sentence)

            # remove all tokens that are not alphabetic
            tokens = [word.strip() for word in tokens if word.isalpha()]

            self.sentences.append(tokens)

    def comment_changed(self) -> bool:
        """
        Return True if the commit fixes a comment.

        Returns
        -------
        bool
            True if the commit modifies a comment

        """
        for modification in self.commit.modifications:
            if modification.change_type != ModificationType.MODIFY:
                continue

            diff = [line.strip() for _, line in modification.diff_parsed.get('added', {})]
            diff.extend([line.strip() for _, line in modification.diff_parsed.get('deleted', {})])
            if any(line.startswith('#') for line in diff):
                return True

        return False

    def data_changed(self) -> bool:
        return False

    def include_changed(self) -> bool:
        return False

    def service_changed(self) -> bool:
        return False

    def fixes_conditional(self):
        """
        Return True if the commit fixes a conditional.

        Returns
        -------
        bool
            True if the commit fixes a conditional. False, otherwise.

        """
        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and rules.has_conditional_pattern(sentence_dep):
                return True

        return False

    def fixes_configuration_data(self):
        """
        Return True if the commit fixes configuration data.

        Returns
        -------
        bool
            True if the commit fixes configuration data. False, otherwise.

        """

        is_data_changed = self.data_changed()

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))

            if rules.has_defect_pattern(sentence) and \
                    (rules.has_storage_configuration_pattern(sentence_dep)
                     or rules.has_file_configuration_pattern(sentence_dep)
                     or rules.has_network_configuration_pattern(sentence_dep)
                     or rules.has_user_configuration_pattern(sentence_dep)
                     or rules.has_cache_configuration_pattern(sentence_dep)
                     or is_data_changed):
                return True

        return False

    def fixes_dependency(self):
        """
        Return True if the commit fixes a dependency.
        For example, if an import or include is changed.

        Returns
        -------
        bool
            True if the commit fixes a dependency. False, otherwise.

        """
        is_include_changed = self.include_changed()

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and (
                    rules.has_dependency_pattern(sentence_dep) or is_include_changed):
                return True

        return False

    def fixes_documentation(self):
        """
        Return True if the commit fixes the documentation.

        Returns
        -------
        bool
            True if the commit fixes the documentation. False, otherwise.

        """

        is_comment_changed = self.comment_changed()

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and (
                    rules.has_documentation_pattern(sentence_dep) or is_comment_changed):
                return True

        return False

    def fixes_idempotency(self):
        """
        Return True if the commit fixes an idempotency issue.

        Returns
        -------
        bool
            True if the commit fixes an idempotency. False, otherwise.

        """

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and rules.has_idempotency_pattern(sentence_dep):
                return True

        return False

    def fixes_security(self):
        """
        Return True if the commit fixes a security issue.

        Returns
        -------
        bool
            True if the commit fixes security. False, otherwise.

        """

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and rules.has_security_pattern(sentence_dep):
                return True

        return False

    def fixes_service(self):
        """
        Return True if the commit fixes a service issue.

        Returns
        -------
        bool
            True if the commit fixes a service. False, otherwise.

        """

        is_service_changed = self.service_changed()

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and (rules.has_service_pattern(sentence_dep) or is_service_changed):
                return True

        return False

    def fixes_syntax(self):
        """
        Return True if the commit fixes a syntax issue.

        Returns
        -------
        bool
            True if the commit fixes syntnax. False, otherwise.

        """

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(utils.get_head_dependents(sentence))
            if rules.has_defect_pattern(sentence) and rules.has_syntax_pattern(sentence_dep):
                return True

        return False
