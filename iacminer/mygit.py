# TODO: handle HTTPSConnectionPool exception

from dotenv import load_dotenv
load_dotenv()

import base64
import os
import github

class Git():
    def __init__(self):
        self.__github = github.Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        print(f'Remaining quota: {self.quota}')

    @property
    def rate_limiting_resettime(self):
        return self.__github.rate_limiting_resettime

    @property
    def quota(self): # search
        return self.__github.rate_limiting[0]

    #@quota_core
    #def quota_core(self):
    #    self.__github.get_rate_limit().core .()

    def get_issues(self, repo: str):
        """ 
        Analyze a repo, returning a generator of closed issues labeled with 'bug'.

        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """
        repo = self.__github.get_repo(repo)

        labels = []
        for label in ('bug', 
                      'Bug',
                      'bug :bug:',
                      'ansible_bug',
                      'Type: Bug',
                      'Type: bug',
                      'type: bug 🐛',
                      'type:bug',
                      'type: bug',
                      'kind/bug',
                      'kind/bugs',
                      'bugfix',
                      'critical-bug',
                      '01 type: bug',
                      'bug_report',
                      'minor-bug'):
            try: 
                labels.append(repo.get_label(label))
            except Exception:
                continue # label not found
        
        for label in labels:
            issues = repo.get_issues(state='closed', labels=[label], sort='created', direction='desc')
            for issue in issues:
                yield issue

        yield


    def get_all_issues(self, repo: str):

        repo = self.__github.get_repo(repo)
        try: 
            issues = repo.get_issues(state='closed', sort='created', direction='desc')
            for issue in issues:
                yield issue
        except Exception:
            pass

        yield
