import github

class Git():
    def __init__(self, token):
        self.__github = github.Github(token)
        print(f'Remaining quota: {self.quota}')

    @property
    def quota_reset_at(self):
        return self.__github.rate_limiting_resettime

    @property
    def quota(self): # search
        return self.__github.rate_limiting[0]

    def get_labels(self, repo: str):
        """
        Get all the labels in a repository
        
        Parameters
        ----------
        repo : str: the repository to analyze (e.g., 'radon-h2020/radon-defect-prediction')

        Returns
        ----------
        labels : set : The set of distinct labels
        """ 
        
        repo = self.__github.get_repo(repo)
        
        labels = set()
        for label in repo.get_labels():
            if type(label) == github.Label.Label:
                labels.add(label.name)

        return labels

    def get_closed_issues(self, repo: str, label:str):
        """
        Get all the closed issues with a given label
        
        Parameters
        ----------
        repo : str: the repository to analyze (e.g., 'radon-h2020/radon-defect-prediction')
        label : str: the label for the issues (e.g., 'bug')

        Returns
        ----------
        issues : list : The list of closed issues with the given label
        """ 
        
        """ 
        Analyze a repo, returning a generator of closed issues labeled with 'bug'.

        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        :label: the label for the issues to search for
        """
        issues = list()
        repo = self.__github.get_repo(repo)
        label = repo.get_label(label)
        for issue in repo.get_issues(state='closed', labels=[label], sort='created', direction='desc'):
            issues.append(issue)

        return issues