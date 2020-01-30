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
    """
    def __check_rate_limit(self):
        print(self.__github.rate_limiting)
        print(self.__github.rate_limiting_resettime)
        return self.__github.rate_limiting_resettime
    """
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

    def get_commits(self, repo: str):
        """ 
        Analyze a repo, returning a generator of commits.

        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        """
        repo = self.__github.get_repo(repo)
        for commit in repo.get_commits():
            yield commit

    def get_commit(self, repo: str, sha: str) -> github.Commit:
        """ 
        Return the specified commit from the repo, if exists
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        :sha: the commit id to find

        :return: github.Commit the commit. None if not found.
        """
        repo = self.__github.get_repo(repo)
        commit_page_list = repo.get_commits(sha=sha)

        commit = None
        if commit_page_list.totalCount > 0:
            commit = commit_page_list.get_page(0)[0]
        
        return commit

    def get_git_blob(self, repo: str, sha: str):
        """
        :repo: string
        :sha: string
        :rtype: string
        """
        repo = self.__github.get_repo(repo)
        blob = repo.get_git_blob(sha)
        decoded_content = base64.b64decode(blob.content).decode('utf-8')
        return decoded_content
        
    def get_contents(self, repo: str, path: str, ref: str=None):
        """
        Analyze all the files of a repo, returning a generator of content files.
        
        :repo: a repository 'author/repository' (e.g. 'PyGithub/PyGithub')
        :path: the path to search in
        :ref: the commit sha where to get the files. If None the master is considered
        """
        repo = self.__github.get_repo(repo)
        dirs_stack = [path]
        
        while len(dirs_stack):
            path = dirs_stack.pop()
            contents = repo.get_contents(path=path, ref=ref)
            
            if type(contents) is github.ContentFile.ContentFile:
                yield contents

            elif type(contents) is list:
                for content in contents:
                    if content.type == 'dir':
                        dirs_stack.append(os.path.join(path, content.name))
                    else:
                        yield content