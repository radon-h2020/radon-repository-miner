# Mine

`radon-miner -h`

```text
usage: radon-miner mine [-h] [--branch BRANCH] [--verbose] path_to_repo {github,gitlab} {ansible,tosca} full_name_or_id dest

positional arguments:
  path_to_repo     the local path to the git repository
  {github,gitlab}  the source code versioning host
  {ansible,tosca}  mine only commits modifying files of this language
  full_name_or_id  the repository full name or id (e.g., radon-h2020/radon-repository-miner
  dest             destination folder for the reports

optional arguments:
  -h, --help       show this help message and exit
  --branch BRANCH  the repository branch to mine (default: master)
  --verbose        show log
```

## path_to_repo
The path to the cloned repository. This is mandatory to execute the SZZ algorithm to identify bug-inducing-commits.

## host {github, gitlab}
The SVM hosting platform. Currently, Github and Gitlab are supported.

## language {ansible, tosca}
The language to consider during mining. Currently, Ansible and Tosca are supported.

## full_name_or_id
The full name of the repository (`<owner/name>`) or its id (e.g., `radon-h2020/radon-repository-miner`).

## dest
The path to a folder where to save the reports: 

* an HTML report accessible at `path/to/reports/report.html`
* a JSON report accessible at `path/to/reports/report.json`


# Examples

Clone the [adriagalin/ansible.motd](https://github.com/adriagalin/ansible.motd.git) repository: 

`git clone https://github.com/adriagalin/ansible.motd.git`

From the same folder, create a folder for reports: 

`mkdir mining_reports/`

 
 and run the command:

```text 
radon-miner ansible.motd github ansible adriagalin/ansible.motd mining_reports

Access token: ******
```

As can be seen, the tool will prompt the user for the Github access token (or Gitlab access tokne if option `gitlab`).
See how to get one for [Github](https://github.com/settings/tokens) and [Gitlab](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
Copy-pasting the token and pressing enter will start the mining.

!!! note
    You might avoid this step (for example because want to automate the process in CI/CD).
    In that case, add `GITHUB_ACCESS_TOKEN` and `GITLAB_ACCESS_TOKEN` in the environment variables by: 
   
    `export GITHUB_ACCESS_TOKEN=***********` <br>
    `export GITLAB_ACCESS_TOKEN=***********`
    

You can now access the reports:

```
cd mining_reports/
ls

report.html report.json
```  

