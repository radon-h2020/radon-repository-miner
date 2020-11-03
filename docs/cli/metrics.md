# Extract metrics

```text
usage: repo-miner extract-metrics [-h] [--verbose] path_to_repo src {ansible,tosca} {product,process,delta,all} {release,commit} dest

positional arguments:
  path_to_repo          the absolute path to a cloned repository or the url to a remote repository
  src                   the json report generated from a previous run of 'repo-miner mine'
  {ansible,tosca}       extract metrics for Ansible or Tosca
  {product,process,delta,all}
                        the metrics to extract
  {release,commit}      extract metrics at each release or commit
  dest                  destination folder to save the resulting csv

optional arguments:
  -h, --help            show this help message and exit
  --verbose        show log
```

!!! note "Output"
    This command generate a `metrics.csv` file in folder `dest`.

!!! warning "Requirements"
    If passing a remote `path_to_repo`, such as `https://github.com/radon-h2020/radon-repository-miner.git`, you **MUST** 
    add the following to your environment variables: 

    * `TMP_REPOSITORIES_DIR=<path/to/tmp/repositories/>` to temporary clone the remote repository for the analysis. 
    Please, note that the repository will be cloned in thisa folder but not deleted. The latter step is left to the user,
    when and if needed. 

The following metrics can be extracted per each `release` or `commit`:

* `product`: **product metrics** measure structural characteristics of code scripts (such as *lines of code*, *number of
 conditions*, *number of tasks*, etc.), and are extracted using [`radon-ansible-metrics`](https://github.com/radon-h2020/radon-ansible-metrics) and [`radon-tosca-metrics`](https://github.com/radon-h2020/radon-tosca-metrics) 
for `ansible` and `tosca`, respectively.

* `process`: **process metrics** measure aspects of the development process rather than the characteristic of code (such
as the *number of commits*, *number of files committed together*, *added and removed lines*, etc.), and are extracted by
the [`ishepard/pydriller`](https://pydriller.readthedocs.io/en/latest/processmetrics.html).

* `delta`: **delta metrics** are calculated as the difference of each metric between two successive releases or commits.



# Example

Follow the [mine example](https://radon-h2020.github.io/radon-repository-miner/cli/mine/#Example) in the previous 
section to generate the `failure-prone-files.json`.

Afterwards, extract metrics as follow.

## Using Docker
    
1. **Extract metrics**
    
    `docker run -v /tmp/repo-miner:/app repo-miner:latest repo-miner extract-metrics repo-miner-env/tmp/ansible.motd ./failure_prone_files.json ansible all release . --verbose`
    
    or (passing the url to repository)
    
    `docker run -v /tmp/repo-miner:/app repo-miner:latest repo-miner extract-metrics https://github.com/adriagalin/ansible.motd.git ./failure_prone_files.json ansible all release . --verbose`

2. **Access reports**
    
    `ls /tmp/repo-miner`



## Using the CLI on local machine

1. **Move (or stay) in the working directory**

    `cd radon-example`
    
2. **Extract metrics**

    `repo-miner extract-metrics repo-miner-env/tmp/ansible.motd ./failure_prone_files.json ansible all release . --verbose`

3. **Access results**
    
    `ls .`


You can now see that `metrics.csv` has been added to the folder:



---

In both cases, you should get a similar output:

```text
Extracting metrics from repo-miner-env/tmp/ansible.motd using report ./failure_prone_files.json [started at: 17:34]
Setting up ansible metrics extractor
Extracting all metrics
Metrics saved at ./metrics.csv [completed at: 17:35]
```

The results directory should contain the following files:

```text
failure-prone-files.html failure-prone-files.json metrics.csv
```  