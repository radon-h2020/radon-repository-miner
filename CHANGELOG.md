# CHANGELOG

## [0.8.12]
- Enhancement: Added functionality to compute delta metrics between two successive releases

## [0.8.11]
- Bugfix: Caught missing TypeError that made the program fail when executing AnsibleMetrics on an empty script

## [0.8.10]
- Bugfix UnicodeDecodeError when reading file content

## [0.8.9]
- Updated dependency to AnsibleMetrics (0.3.8)

## [0.8.7]
- Updated discard of undesired commits and ansible file recognition

## [0.8.6]
- Bugfix: ValueError: invalid literal for int() with base 10: ''

## [0.8.3]
- Added cli option (--include-commits) to include a list of fixing-commits. The purpose is to save time during future
analyses.
- Upgraded dependencies.

## [0.8.0]
- Added two more options to the CLI to mine fixing-commits and fixed-files
- Refactored application

## [0.5.0]
- Changed command-line options
- Changed APIs parameters in miners and metrics_extractors

## [0.3.0]
- Renamed modules (repository -> mining.ansible, mining.tosca).
- RepositoryMiner is now BaseMiner in mining.base, and is extended by AnsibleMiner in mining.ansible and ToscaMiner in mining.tosca.
- Command-line changes (see the updated docs for usage).
- Refactoring.

## [0.2.10]
- It is now possible to set up a list of fixing-files to exclude from mining.

## [0.2.9]
- It is now possible to set up a list of commits to ignore before mining.

## [0.2.8]
- Added conditions in get_fixing_commits_from_* to speed up execution when fixing-commits are provided in advance. 
In this way, the miner avoid parsing commit messages for those commits already known to be fixing-commits.

## [0.2.7]
- Bugfix.

## [0.2.6]
- Bugfix.
  
## [0.2.5]
- The module miner has been renamed to repositoryminer, to avoid misleading imports in third-party applications.
  
  **Important:** be sure to rename *import miner* into *import repositoryminer* in your code.

## [0.2.4]
- Bug-fixing

## [0.2.3]
- Bug-fixing

## [0.2.2]
- Fixed minor bugs

## [0.2.1]
- Replaced issues in get_closed_issues from set to list to fix error 'Unashable type: Issue'

## [0.2.0]
- Released new standalone version. GithubMiner is not supported anymore and has been moved to its own repository.

## [0.1.3]
- The mine-repository option is now supported

## [0.1.2]
- Removed unused dependencies

## [0.1.1]
- Fixed excepton catching

## [0.1]
- Added command-line interface

## [0.0.2]
- First working release