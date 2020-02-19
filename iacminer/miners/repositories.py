"""
A module to get information of repositories
"""
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import os
import re
from datetime import datetime, timedelta

from iacminer.configuration import Configuration
from iacminer.entities.repository import Repository

token = os.getenv('GITHUB_ACCESS_TOKEN')
HEADERS = {'Authorization': f'token {token}'} 

class RepositoryMiner():

    def __init__(self, configuration:Configuration):
        self.config = configuration

        # First commit ansible/Ansible Feb 23 14:17:24 2012
        self.date_from = self.config.date_from
        self.date_to = self.__update_delta(self.date_from) # = date_from + self.config.timedelta
        self.date_end = self.config.date_to

        # data
        self.remaining_calls = 1 

    def __update_delta(self, date):
        """
        Update a date by the timedelta defined in self.config
        """
        date = date.replace('T', ' ').replace('Z', '')
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date += timedelta(hours=self.config.timedelta)
        date = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return date

    def __update_dates(self):
        self.date_from = self.__update_delta(self.date_from)
        self.date_to = self.__update_delta(self.date_to)

    def __run_query(self, query): 
        """
        Run a graphql query 
        """
        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=HEADERS)
        if request.status_code == 200:
            return request.json()
        else:
            print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
            return None
    
    def is_ansible_dir(self, d):
        return d.get('name') in ['tasks', 'playbooks', 'handlers', 'roles', 'meta'] and d.get('type') == 'tree'

    def __filter_repositories(self, edges):
        for node in edges:
            node = node.get('node', {})

            has_issues_enabled = node.get('hasIssuesEnabled', True)
            has_issues = node.get('issues', {}).get('totalCount', 0) > 0
            has_releases = node.get('releases', {}).get('totalCount', 0) > 0 
            is_archived = node.get('isArchived', False)
            is_disabled = node.get('isDisabled', False)
            is_mirror = node.get('isMirror', False)
            is_fork = node.get('isFork', False)
            is_locked = node.get('isLocked', False)
            is_template = node.get('isTemplate', False)
            is_active = node.get('pushedAt') >= self.config.pushed_after

            if not has_issues_enabled:
                continue

            if is_archived or is_disabled or is_mirror or is_fork or is_locked or is_template:
                continue

            if not has_issues:
                continue

            if not has_releases:
                continue

            if not is_active:
                continue

            node['defaultBranchRef'] = node.get('defaultBranchRef', {}).get('name')
            node['owner'] = node.get('owner', {}).get('login')
            node['stargazers'] = node.get('stargazers', {}).get('totalCount')
            node['watchers'] = node.get('watchers', {}).get('totalCount')
            node['releases'] = node.get('releases', {}).get('totalCount')
            node['issues'] = node.get('issues', {}).get('totalCount')

            yield node

    def mine(self):
        
        while self.remaining_calls > 0 and self.date_from <= self.date_end:
            print(f'From: {self.date_from} to {self.date_to}')
            
            has_next_page = True
            end_cursor = None

            while self.remaining_calls > 0 and has_next_page:
                query = re.sub('DATE_FROM', self.date_from, self.config.query) 
                query = re.sub('DATE_TO', self.date_to, query) 
                query = re.sub('AFTER', '', query) if not end_cursor else re.sub('AFTER', f', after: "{end_cursor}"', query)

                """
                print(f'Searching after: {str(end_cursor)}')
                print(str(query[2:150]).strip())
                """
                result = self.__run_query(query) # Execute the query
                print(f'Remaining calls: {self.remaining_calls}')
            
                if not result:
                    break
                
                self.remaining_calls = int(result['data']['rateLimit']['remaining'])

                has_next_page = bool(result['data']['search']['pageInfo']['hasNextPage'])
                end_cursor = str(result['data']['search']['pageInfo']['endCursor'])

                edges = result.get('data', {}).get('search', {}).get('edges', [])

                for node in self.__filter_repositories(edges):

                    yield Repository(id=node.get('id'),
                                     default_branch=node.get('defaultBranchRef'),
                                     owner=node.get('owner'),
                                     name=node.get('name'),
                                     url=node.get('url'),
                                     primary_language=node.get('primaryLanguage', {}).get('name'),
                                     created_at=node.get('createdAt'),
                                     pushed_at=node.get('pushedAt'),
                                     stars=int(node.get('stargazers', 0)),
                                     releases=int(node.get('releases', 0)),
                                     issues=int(node.get('issues', 0)))

            #print('\033c')
            self.__update_dates()
