import json

class Repository():

    def __init__(self, 
                 id: str,
                 default_branch: str,
                 owner: str,
                 name: str,
                 url: str,
                 primary_language: str,
                 created_at: str,
                 pushed_at: str,
                 stars: int,
                 watchers: int,
                 releases: int,
                 issues: int):

        self.id = id
        self.default_branch = default_branch
        self.owner = owner
        self.name = name
        self.remote_path = f'{owner}/{name}'
        self.primary_language = primary_language
        self.created_at = created_at
        self.pushed_at = pushed_at
        self.stars = stars
        self.watchers = watchers
        self.releases = releases
        self.issues = issues

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Repository):
            return self.id == other.id
                   
        return False

class RepositoryEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Repository):
            return obj.__dict__

        elif isinstance(obj, list):
            json_obj = []
            for item in obj:
                json_obj.append(json.dumps(item, cls=RepositoryEncoder))

            return json_obj

        return super(RepositoryEncoder, self).default(obj)

class RepositoryDecoder(json.JSONDecoder):
    
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.json_to_object)
    
    def json_to_object(self, dict):
        
        return Repository(id=dict.get('id'),
                          default_branch=str(dict.get('defaultBranchRef')),
                          owner=str(dict.get('owner')),
                          name=str(dict.get('name')),
                          url=str(dict.get('url')),
                          primary_language=str(dict.get('primaryLanguage')),
                          created_at=str(dict.get('createdAt')),
                          pushed_at=str(dict.get('pushedAt')),
                          stars=int(dict.get('stargazers', 0)),
                          watchers=int(dict.get('watchers', 0)),
                          releases=int(dict.get('releases', 0)),
                          issues=int(dict.get('issues', 0)))
