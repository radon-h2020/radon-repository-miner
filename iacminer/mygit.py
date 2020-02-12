# TODO: handle HTTPSConnectionPool exception

from dotenv import load_dotenv
load_dotenv()

import base64
import os
import github

class Git():
    def __init__(self):
        self.__github = github.Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        print(f'Remaining quota: {self.get_remaining_quota()}')

    @property
    def rate_limiting_resettime(self):
        return self.__github.rate_limiting_resettime

    def get_remaining_quota(self):
        return self.__github.rate_limiting[0]

    def get_issues(self, repo: str):
        """ 
        Analyze a repo, returning a generator of closed issues labeled with 'bug'.

        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """
        repo = self.__github.get_repo(repo)

        try: 
            label_bug = repo.get_label('Bug')

            issues = repo.get_issues(state='closed', labels=[label_bug], sort='created', direction='desc')
            for issue in issues:
                yield issue

        except Exception:
            yield