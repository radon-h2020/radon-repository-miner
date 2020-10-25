# Extract metrics

```text
usage: radon-miner extract-metrics [-h] [--verbose] path_to_repo src {ansible,tosca} {product,process,delta,all} {release,commit} dest

positional arguments:
  path_to_repo          the absolute path to a cloned repository or the url to a remote repository
  src                   the json report generated from a previous run of 'radon-miner mine'
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


## Examples

Follows one of the [examples](https://radon-h2020.github.io/radon-repository-miner/cli/mine/#Examples) in the previous 
section to generate the `failure-prone-files.json`.

Afterwards, run:

`radon-miner extract-metrics radon-miner-env/tmp/ansible.motd ./failure_prone_files.json ansible all release . --verbose`

You should get a similar output:

```text
Extracting metrics from radon-miner-env/tmp/ansible.motd using report ./failure_prone_files.json [started at: 17:34]
Setting up ansible metrics extractor
Extracting all metrics
Metrics saved at ./metrics.csv [completed at: 17:35]
```

You can now see that `metrics.csv` has been added to the folder:

```text
ls

failure-prone-files.html failure-prone-files.json metrics.csv
```  
