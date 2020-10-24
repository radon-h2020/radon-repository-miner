# API Reference
   
*  **```self.exclude_commits: List[str]```**  - There may be several false-positives among the identified fixing-commits. 
This variable is used to set up in advance the commits to exclude during the mining.
   
*  **```self.exclude_fixing_files: Lists[FixingFile]```**  - There may be several false-positives among the identified fixing-files. 
This variable is used to set up in advance the files to exclude during the mining for a given commit.

*  **```self.fixing_commits: List[str]```**  - Contains the commits that are supposed to fix a bug according to the labels and regex passed by the user. 
   These are set up during the mining, although it can be defined in advance to speed up the mining avoiding to analyze commits that are already present here.

*  **```self.fixing_files: List[FixingFiles]```**  - Contains the files modified i fixing-commits.

*  **```discard_non_iac_fixing_commits(commits: List[str])```**  - Given a list of commits, discard commits that do not modify IaC files (i.e., Ansible).
*  **```get_labels() -> Set[str]```**  - Get al the issue labels in the repository.
*  **```get_closed_issues(label: str) -> Set[Issue]```**  - Get all the closed issues with a given label.
*  **```get_fixing_commits_from_closed_issues(labels: Set[str]) -> List[str]```**  - Collect fixing-commit hashes by analyzing closed issues related to bugs.
*  **```get_fixing_commits_from_commit_messages(regex: str) -> List[str]```**  - Collect fixing-commit hashes by analyzing commit messages.
*  **```get_fixing_files() -> List[FixingFile]```**  - Collect the IaC files involved in fixing-commits and for each of them identify the bug-inducing-commit.
*  **```label() -> Generator[LabeledFile, None, None]```**  - Start labeling process.
