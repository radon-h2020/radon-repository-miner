from dotenv import load_dotenv
load_dotenv()

import os
import github

class Git():
    
    def __init__(self):
        self.__github = github.Github(os.getenv('GITHUB_ACCESS_TOKEN'))

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








##################
  
    

    def get_files(self, repo, path, ref=None):
        repository = self.__github.get_repo(repo)
        files = []
        contents = repository.get_contents(path=path, ref=ref)
        for c in contents:
            if ('playbooks' in c.path or 'meta' in c.path or 'tasks' in c.path or 'handlers' in c.path or 'roles' in c.path):
                if c.type == 'dir':
                    files.extend(self.get_files(repo, path=path + '/' + c.name, ref=ref))
                elif c.type == 'file' and c.path.endswith('.yml'):
                    files.append({'filename': c.path, 
                                  'decoded_content': c.decoded_content, 
                                  'sha': c.sha})

        return files   
    