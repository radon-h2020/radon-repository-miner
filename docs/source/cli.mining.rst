Mining using Command-Line
#########################


.. code-block:: RST

    usage: repo-miner mine [-h] [--branch BRANCH] [--exclude-commits EXCLUDE_COMMITS] [--exclude-files EXCLUDE_FILES] [--verbose] {fixing-commits,fixed-files,failure-prone-files} {github,gitlab} {ansible,tosca} repository dest

    positional arguments:
      {fixing-commits,fixed-files,failure-prone-files}
                            the information to mine
      {github,gitlab}       the source code versioning host
      {ansible,tosca}       mine only commits modifying files of this language
      repository            the repository full name: <onwer/name> (e.g., radon-h2020/radon-repository-miner)
      dest                  destination folder for the reports

    optional arguments:
      -h, --help            show this help message and exit
      -b, --branch BRANCH   the repository branch to mine (default: master)
      --exclude-commits EXCLUDE_COMMITS
                            the path to a JSON file containing the list of commit hashes to exclude
      --include-commits INCLUDE_COMMITS
                            the path to a JSON file containing the list of commit hashes to include
      --exclude-files EXCLUDE_FILES
                            the path to a JSON file containing the list of FixedFiles to exclude
      --verbose             show log

.. note::

    Running this command will generate the following report files:

    * ``dest/fixing-commits.json`` containing the list of fixing-commit hashes;

    * ``dest/fixed-files.json`` containing the list of FixedFile objects (if mined `fixed-files` or `failure-prone-files`);

    * ``dest/failure-prone-files.json`` containing the list of FailureProne objects (if mined `failure-prone-files`);


.. warning::

    To properly use this command you **MUST** add the following to your environment variable:

    * ``TMP_REPOSITORIES_DIR=<path/to/tmp/repositories/>`` to temporary clone the remote repository for analysis. Please, note that the repository will be cloned in this folder but not deleted. The latter step is left to the user, when and if needed. **Note:** this variable is not needed if using the Docker image.




Examples
========

Using Docker
************

1. **Pull the Docker image**

    ``docker pull radonconsortium/repo-miner:latest``

2. **Create a folder to share results**

    ``mkdir /tmp/repo-miner``

3. **Mine**

    *(using github)*

    .. code-block:: RST

        docker run -v /tmp/repo-miner:/app  -e GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:latest repo-miner mine failure-prone-files github ansible adriagalin/ansible.motd . --verbose

    *(using gitlab)*

    .. code-block:: RST

        docker run -v /tmp/repo-miner:/app  -e GITLAB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN repo-miner:latest repo-miner mine failure-prone-files github ansible adriagalin/ansible.motd . --verbose

5. **Access reports**

    ``ls /tmp/repo-miner``




On local machine
****************

1. **Setup environment variables**

    ``export GITHUB_ACCESS_TOKEN=*****``

    ``export GITLAB_ACCESS_TOKEN=*****``

    ``export TMP_REPOSITORIES_DIR=/tmp/``

2. **Create a working directory and move there**

    ``mkdir radon-example && cd radon-example``

3. **(Optional) Create a virtualenv to avoid affecting the original environment**

    .. code-block:: RST

        sudo apt install python3-venv
        python3 -m venv repo-miner-env
        source repo-miner-env/bin/activate

4. **Install the package**

    ``pip install repository-miner``

5. **Mine**

    ``repo-miner mine failure-prone-files github ansible adriagalin/ansible.motd . --verbose``

6. **Access reports**

    ``ls .`` (Recall the working directory is ``radon-example``)




Either way, you'll get a similar output:

.. code-block:: RST

    Mining adriagalin/ansible.motd [started at: 15:29]
    Identifying fixing-commits from closed issues related to bugs
    Identifying fixing-commits from commit messages
    Saving fixing-commits
    JSON created at ./fixing-commits.json
    Identifying ansible files modified in fixing-commits
    Saving fixed-files
    JSON created at ./fixed-files.json
    Identifying and labeling failure-prone files
    Saving failure-prone files
    JSON created at ./failure-prone-files.json
