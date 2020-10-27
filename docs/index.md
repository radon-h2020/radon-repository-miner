# How to install

From [PyPI](https://pypi.org/project/repository-miner/):

```pip install repository-miner```

From source code:

```text
git clone https://github.com/radon-h2020/radon-repository-miner.git
cd radon-repository-miner
pip install -r requirements.txt
pip install .
```

# How to test

To avoid affecting the current environment, it is strongly recommended to create and activate a virtual environment:

```
sudo apt install python3-venv
python3 -m venv repo-miner-env
source repo-miner-env/bin/activate
```

Setup environment variables:

```text
export GITHUB_ACCESS_TOKEN=************
export GITLAB_ACCESS_TOKEN=************
```

Then

```text
pip install pytest
pip install -r requirements.txt
pip install .
unzip test_data.zip -d .
pytest tests/
```

