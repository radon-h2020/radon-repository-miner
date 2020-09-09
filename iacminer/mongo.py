from pymongo import MongoClient


class MongoDBManager:

    def __init__(self, host: str, port: int):
        self.client = MongoClient(host, port)
        self.db = self.client['iac_miner']

    def db_exists(self) -> bool:
        return 'iac_miner' in self.client.list_database_names()

    def get_all_repos(self) -> list:
        return [document for document in self.db.repositories.find({})]

    def get_single_repo(self, _id: str):
        return self.db.repositories.find_one({'_id': _id})

    def add_repo(self, repo: dict):
        repo_id = self.db.repositories.insert_one(repo).inserted_id
        return repo_id

    def replace_repo(self, repo: dict):
        return self.db.repositories.replace_one({'_id': repo['_id']}, repo)


"""
iac_miner = MongoDBManager('localhost', 27017)

iac_miner.client.drop_database('iac_miner')
iac_miner.add_repo({
    '_id': 'Test1',
    'default_branch': 'master',
    'owner': 'stefano',
    'name': 'my-first-repo',
    'url': 'none',
    'description': 'this is another description',
    'issues': 47,
    'releases': 160,
    'stars' : 19,
    'watchers' : 29,
    'primary_language': 'python'
})
iac_miner.add_repo({
    '_id': 'Test2',
    'default_branch': 'master',
    'owner': 'stefano',
    'name': 'my-first-repo',
    'url': 'none',
    'description': 'this is another description',
    'issues': 47,
    'releases': 160,
    'stars' : 19,
    'watchers' : 29,
    'primary_language': 'python'
})


previous = iac_miner.replace_repo({
    '_id': 'Test1',
    'default_branch': 'master',
    'owner': 'stefano',
    'name': 'my-second-repo'
})

print(iac_miner.get_all_repos())

# delete database
# iac_miner.client.drop_database('iac_miner')

"""