# Mine

```text
usage: radon-miner mine [-h] [--branch BRANCH] [--verbose] {github,gitlab} {ansible,tosca} repository dest

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
    
    * `dest/report.html`
    * `dest/report.json`

!!! warning "Requirements"
    To properly use this command you **MUST** add the following to your environment variables: 
   
    * `GITHUB_ACCESS_TOKEN=<paste your token here>` if you are using the `github` argument. See how to create a personal 
    access token [here](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).
    
    * `GITLAB_ACCESS_TOKEN=<paste your token here>` if you are using the `gitlab` argument. See how to create a personal 
    access token [here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
    
    * `TMP_REPOSITORIES_DIR=<path/to/tmp/repositories/>` to temporary clone the remote repository for analysis. 
    Please, note that the repository will be cloned in this folder but not deleted. The latter step is left to the user,
    when and if needed. 
    


# Examples

## Mine repository (using a venv)
For the sake of the example, let's create and move to an example directory:
 
`mkdir radon-example && cd radon-example`

To avoid affecting the original environment, create a new virtual environment:

```text
sudo apt install python3-venv
python3 -m venv radon-miner-env
source radon-miner-env/bin/activate
```

Create a `tmp` folder to clone the repositories to analyze:

```text
mkdir radon-miner-env/tmp
ls radon-miner-env/

bin  include  lib  lib64  pyvenv.cfg  share  tmp
```

Set up the environment variables required by the tool:

```text
export GITHUB_ACCESS_TOKEN=***************
export TMP_REPOSITORIES_DIR=./radon-miner-env/tmp/
``` 

Install the package:

`pip install radon-repository-miner`

Finally, run:

```text
radon-miner mine github ansible adriagalin/ansible.motd . --verbose
```

You should get a similar output:

```text
Mining adriagalin/ansible.motd [started at: 15:29]
Identifying fixing-commits from closed issues related to bugs
Identifying fixing-commits from commit messages
Identifying ansible files modified in fixing-commits
Identifying and labeling failure-prone files
Generating reports
HTML report created at ./report.html
JSON report created at ./report.json
```

You can now see the reports:

```text
ls

report.html report.json
```  

## Mine repository (using the Docker image)