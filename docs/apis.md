# API Reference

*  **```discard_non_iac_fixing_commits(commits: List[str])```**  - Given a list of commits, discard commits that do not modify IaC files (i.e., Ansible).
*  **```get_labels() -> Set[str]```**  - Get al the issue labels in the repository.
*  **```get_closed_issues(label: str) -> Set[Issue]```**  - Get all the closed issues with a given label.
*  **```get_fixing_commits_from_closed_issues(labels: Set[str]) -> List[str]```**  - Collect fixing-commit hashes by analyzing closed issues related to bugs.
*  **```get_fixing_commits_from_commit_messages(regex: str) -> List[str]```**  - Collect fixing-commit hashes by analyzing commit messages.
*  **```get_fixing_files() -> List[FixingFile]```**  - Collect the IaC files involved in fixing-commits and for each of them identify the bug-inducing-commit.
*  **```label() -> Generator[LabeledFile, None, None]```**  - Start labeling process.
*  **```mine(labels: Set[str] = None, regex: str = None) -> Generator[LabeledFile, None, None]```**  - Mine the repository.