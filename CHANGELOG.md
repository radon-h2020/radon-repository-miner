# CHANGELOG

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