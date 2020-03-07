"""
A module to mine Github to extract relevant repositories based on given criteria
"""

import requests
import re
from datetime import datetime

from iacminer.configuration import Configuration
from iacminer.entities.repository import Repository

QUERY = """
{
    search(query: "is:public stars:>=MIN_STARS mirror:false archived:false created:DATE_FROM..DATE_TO", type: REPOSITORY, first: 50 AFTER) {
        repositoryCount
        pageInfo {
            endCursor
            startCursor
            hasNextPage
        }
        edges {
            node {
                ... on Repository {
                    id
                    defaultBranchRef { name }
                    owner { login }
                    name
                    url
                    description
                    primaryLanguage { name }
                    collaborators { totalCount }
                    stargazers { totalCount }
                    watchers { totalCount }
                    releases { totalCount }
                    issues { totalCount }
                    createdAt
                    pushedAt
                    updatedAt
                    hasIssuesEnabled
                    isArchived
                    isDisabled
                    isMirror
                    isFork
                    object(expression: "master") {
                        ... on Commit {
                            tree {
                                entries {
                                    name
                                    type
                                }
                            }
                            history {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
    }

    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
}
"""

class GithubMiner():

    def __init__(self, 
                 date_from: datetime, 
                 date_to: datetime,
                 pushed_after: datetime=None,
                 min_stars: int=0,
                 min_releases: int=0,
                 min_collaborators: int=0,
                 min_watchers: int=0,
                 primary_language: str=None,
                 include_fork: bool=False
                ):

        self.date_from = date_from.strftime('%Y-%m-%dT%H:%M:%SZ') 
        self.date_to = date_to.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.pushed_after = pushed_after.strftime('%Y-%m-%dT%H:%M:%SZ') if pushed_after else ''
        self.min_stars = min_stars
        self.min_releases = min_releases
        self.min_collaborators = min_collaborators
        self.min_watchers = min_watchers
        self.primary_language = primary_language
        self.include_fork = include_fork
        
        self._quota = 0

        self.query = re.sub('MIN_STARS', str(self.min_stars), QUERY)
        self.query = re.sub('DATE_FROM', str(self.date_from), self.query) 
        self.query = re.sub('DATE_TO', str(self.date_to), self.query) 

    def set_token(self, access_token:str):
        self.__token = access_token

    @property
    def quota(self):
        return self._quota

    @property
    def quota_reset_at(self):
        return self._quota_reset_at

    def run_query(self): 
        """
        Run a graphql query 
        """
        request = requests.post('https://api.github.com/graphql', json={'query': self.query}, headers={'Authorization': f'token {self.__token}'})
        if request.status_code == 200:
            return request.json()
        else:
            print("Query failed to run by returning code of {}. {}".format(request.status_code, self.query))
            return None
    
    def is_ansible_dir(self, d):
        return d.get('name') in ['tasks', 'playbooks', 'handlers', 'roles', 'meta'] and d.get('type') == 'tree'

    def filter_repositories(self, edges):

        for node in edges:
            
            node = node.get('node')

            if not node:
                continue
            
            has_issues_enabled = node.get('hasIssuesEnabled', True)
            collaborators = node['collaborators']['totalCount'] if node['collaborators'] else 0 
            issues = node['issues']['totalCount'] if node['issues'] else 0
            releases = node['releases']['totalCount'] if node['releases'] else 0
            stars = node['stargazers']['totalCount'] if node['stargazers'] else 0
            watchers = node['watchers']['totalCount'] if node['watchers'] else 0
            is_active = node.get('pushedAt', '') >= self.pushed_after or node.get('createdAt', '') >= self.pushed_after
            is_disabled = node.get('isDisabled', False)
            is_fork = node.get('isFork', False)
            is_locked = node.get('isLocked', False)
            is_template = node.get('isTemplate', False)
            primary_language = node['primaryLanguage']['name'] if node['primaryLanguage'] else ''
            
            if not has_issues_enabled:
                continue
            
            if collaborators < self.min_collaborators:
                continue

            if issues == 0:
                continue

            if releases < self.min_releases:
                continue

            if watchers < self.min_watchers:
                continue
            
            if is_disabled or is_locked or is_template:
                continue
            
            if self.primary_language and self.primary_language != primary_language:
                continue

            if not is_active:
                continue
            
            if not self.include_fork and is_fork:
                continue

            object = node.get('object')
            if not object:
                continue

            #entries = object.get('tree', {}).get('entries', [])
            #if not any([self.is_ansible_dir(entry) for entry in entries]):
            #    continue
            
            yield dict(
                    id=node.get('id'),
                    default_branch=node.get('defaultBranchRef', {}).get('name'),
                    owner=node.get('owner', {}).get('login'),
                    name=node.get('name'),
                    url=node.get('url'),
                    collaborators=collaborators,
                    issues=issues,
                    releases=releases,
                    stars=stars,
                    watchers=watchers,
                    primary_language=primary_language,
                    created_at=str(node.get('createdAt')),
                    pushed_at=str(node.get('pushedAt'))
            )

    def mine(self):
        
        has_next_page = True
        end_cursor = None

        while has_next_page:
            
            self.query = re.sub('AFTER', '', self.query) if not end_cursor else re.sub('AFTER', f', after: "{end_cursor}"', self.query)

            result = self.run_query()
            
            if not result:
                break
            
            if not result.get('data'):
                break

            if not result['data'].get('search'):
                break
            
            self._quota = int(result['data']['rateLimit']['remaining'])
            self._quota_reset_at = result['data']['rateLimit']['resetAt']

            has_next_page = bool(result['data']['search']['pageInfo'].get('hasNextPage'))
            end_cursor = str(result['data']['search']['pageInfo'].get('endCursor'))

            edges = result['data']['search'].get('edges', [])

            for repo in self.filter_repositories(edges):
                yield repo
