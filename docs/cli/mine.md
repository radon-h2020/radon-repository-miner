# Mine

```text
usage: repo-miner mine [-h] [--branch BRANCH] [--verbose] {github,gitlab} {ansible,tosca} repository dest

positional arguments:
  {github,gitlab}  the source code versioning host
  {ansible,tosca}  mine only commits modifying files of this language
  repository       the repository full name: <onwer/name> (e.g., radon-h2020/radon-repository-miner) 
  dest             destination folder for the reports

optional arguments:
  -h, --help       show this help message and exit
  --branch BRANCH  the repository branch to mine (default: master)
  --verbose        show log
```

!!! note "Output"
    Running this command will generate the following report files:
    
    * `dest/failure-prone-files.html`
    * `dest/failure-prone-files.json`
    
    File `failure-prone-files.json` is a list of dictionaries containing the `filepath` relative to the repository root,
    the `commit` hash at which the file was failure-prone, and the respective `fixing-commit` hash.

!!! warning "Requirements"
    To properly use this command you **MUST** add the following to your environment variables: 
   
    * `GITHUB_ACCESS_TOKEN=<paste your token here>` if you are using the `github` argument. See how to create a personal 
    access token [here](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).
    
    * `GITLAB_ACCESS_TOKEN=<paste your token here>` if you are using the `gitlab` argument. See how to create a personal 
    access token [here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
    
    * `TMP_REPOSITORIES_DIR=<path/to/tmp/repositories/>` to temporary clone the remote repository for analysis. 
    Please, note that the repository will be cloned in this folder but not deleted. The latter step is left to the user,
    when and if needed. 
    


# Example

## Using Docker

1. **Setup environment variables**

    `export GITHUB_ACCESS_TOKEN=***************` 
    
    `export GITLAB_ACCESS_TOKEN=***************` 

2. **Pull the Docker image**

    `docker pull radonconsortium/repo-miner:latest`

3. **Create a folder to share results**
    
    `mkdir /tmp/repo-miner`
    
4. **Mine**
    
    *(using github)* `docker run -v /tmp/repo-miner:/app  -e GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:latest repo-miner mine github ansible adriagalin/ansible.motd . --verbose`
    
    *(using gitlab)* `docker run -v /tmp/repo-miner:/app  -e GITLAB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:latest repo-miner mine github ansible adriagalin/ansible.motd . --verbose`

5. **Access reports**
    
    `ls /tmp/repo-miner`




## Using the CLI on local machine

1. **Setup environment variables**

    `export GITHUB_ACCESS_TOKEN=***************` 
    
    `export GITLAB_ACCESS_TOKEN=***************` 
    
    `export TMP_REPOSITORIES_DIR=/tmp/` 

2. **Create a working directory and move there**
 
    `mkdir radon-example && cd radon-example`

3. **(Optional) Create a virtualenv to avoid affecting the original environment**

    `sudo apt install python3-venv`<br>
    `python3 -m venv repo-miner-env`<br>
    `source repo-miner-env/bin/activate`

4. **Install the package**

    `pip install repository-miner`

5. **Mine**

    `repo-miner mine github ansible adriagalin/ansible.motd . --verbose`

6. **Access reports**
    
    `ls .` (Recall the working directory is `radon-example`)


---

In both cases you should get a similar output:

```text
Mining adriagalin/ansible.motd [started at: 15:29]
Identifying fixing-commits from closed issues related to bugs
Identifying fixing-commits from commit messages
Identifying ansible files modified in fixing-commits
Identifying and labeling failure-prone files
Generating reports
HTML report created at ./failure-prone-files.html
JSON report created at ./failure-prone-files.json
```
