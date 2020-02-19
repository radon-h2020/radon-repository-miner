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
        self.releases = releases
        self.issues = issues



    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Repository):
            return self.id == other.id
                   
        return False
