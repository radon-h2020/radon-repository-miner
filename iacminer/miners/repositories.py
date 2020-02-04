"""
A module to get information of repositories
TODO: completare
"""

import requests
import json
import os
import re
from datetime import datetime, timedelta

headers = {"Authorization": "token b603dd89b36fe882419ad825ddf72762a564dff0"}

# ...

query = """
{
    search(query: "is:public stars:>10 mirror:false archived:false created:DATE_FROM..DATE_TO", type: REPOSITORY, first: 50 <after>) {
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
                    name
                    url
                    description
                    primaryLanguage { name }
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
                    collaborators { totalCount }
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

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def has_ansible_folders(d):
    return d.get('name') in ['tasks', 'playbooks', 'handlers', 'roles', 'meta'] and d.get('type') == 'tree'
    

if __name__ == '__main__':

    if not os.path.isfile('all_repos.json'):
        open('all_repos.json', 'a').close()

    with open('all_repos.json', 'r') as infile:
        try:
            data = json.load(infile)
        except json.decoder.JSONDecodeError:
            data = {}

    remaining_calls = data.get('rateLimit', {}).get('remaining', 1)
    
    # First commit ansible/Ansible Feb 23 14:17:24 2012
    date_from = data.get('dateFrom', "2014-11-27T00:00:00Z")
    date_to = data.get('dateTo', "2014-11-28T00:00:00Z")

    
    while remaining_calls > 0:

        has_next_page = True
        end_cursor = None
        
        while remaining_calls > 0 and has_next_page:
            modified_query = re.sub('DATE_FROM', date_from, query) 
            modified_query = re.sub('DATE_TO', date_to, modified_query) 

            if not end_cursor:
                modified_query = re.sub('<after>', '', modified_query) 
            else:
                modified_query = re.sub('<after>', ', after: "{}"'.format(str(end_cursor)), modified_query) 

            print(f'Remaining calls: {remaining_calls}')
            print(f'Searching after: {str(end_cursor)}')
            print(modified_query[2:150])
            
            try:
                result = run_query(modified_query) # Execute the query
            except Exception:
                break
                
            data['repositoryCount'] = result["data"]["search"]["repositoryCount"]
            data['pageInfo'] = result["data"]["search"]["pageInfo"]

            repositories = []

            edges = result.get("data", {}).get("search", {}).get("edges", [])
            
            for node in edges:
                node = node.get('node', {})

                has_issues_enabled = node.get("hasIssuesEnabled", True)
                has_issues = node.get('issues', {}).get('totalCount', 0) > 0 
                has_releases = node.get('releases', {}).get('totalCount', 0) > 0 
                is_archived = node.get("isArchived", False)
                is_disabled = node.get("isDisabled", False)
                is_mirror = node.get("isMirror", False)

                #pushedAt = dateutils.parse(node.get('pushedAt'))
                #is_inactive = pushedAt < YYYY-MM-DD?? 
                
                #if is_inactive:
                #    continue

                if not has_issues_enabled:
                    continue
                
                if is_archived or is_disabled or is_mirror:
                    continue

                if not has_issues:
                    continue

                if not has_releases:
                    continue

                object = node.get('object')

                if not object:
                    continue
                
                entries = object.get('tree', {}).get('entries', [])
                
                found = 0
                for entry in entries:
                    if has_ansible_folders(entry):
                        found += 1
                        if entry.get('name') in ['playbooks']:
                            found += 1
                    
                if found >= 2:  # change this number if you want to be more conservative and filter more repos. It was set to 2
                    node['totalCommits'] = object.get('history', {}).get('totalCount', 0)
                    node.pop('object', None)
                    node['ansibleFolders'] = found 
                    repositories.append(node)
                    #break
                    

            current_repos = data.get('repositories', None)
            if not current_repos:
                current_repos = repositories
            elif len(repositories) > 0:
                current_repos.extend(repositories)

            data['repositories'] = current_repos    
            data['rateLimit'] = result["data"]["rateLimit"]
            data['dateFrom'] = date_from
            data['dateTo'] = date_to

            with open('all_repos.json', 'w') as outfile:
                json.dump(data, outfile)

            remaining_calls = int(data['rateLimit']['remaining'])
            has_next_page = bool(data['pageInfo']['hasNextPage'])
            end_cursor = str(data['pageInfo']['endCursor'])
            
        data['totalCount'] = data.get('totalCount', 0) + data.get('repositoryCount', 0)
        
        date_from = date_from.replace('T', ' ').replace('Z', '')
        date_from = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
        date_from += timedelta(hours=24)
        date_from = date_from.strftime('%Y-%m-%dT%H:%M:%SZ')

        date_to = date_from.replace('T', ' ').replace('Z', '')
        date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')  
        date_to += timedelta(hours=24)
        date_to = date_to.strftime('%Y-%m-%dT%H:%M:%SZ')
