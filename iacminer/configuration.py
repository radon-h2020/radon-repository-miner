import os

import re
import yaml 

DEFAULT_STARS = 0
DEFAULT_RELEASES = 0
DEFAULT_MIRROR = 'false'
DEFAULT_ARCHIVED = 'false'

query = """
{
    search(query: "is:public stars:STARS mirror:MIRROR archived:ARCHIVED created:DATE_FROM..DATE_TO", type: REPOSITORY, first: 50 <after>) {
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


class Configuration():
    
    def __init__(self):
        
        if not os.path.isfile('./config.yml'):
            raise Exception('No config.yml found')

        with open('./config.yml', 'r') as in_file:
            self.__yml = yaml.safe_load(in_file.read())
       
    @property
    def build_query(self):
        self.__query = re.sub('STARS', self.stars, query)
        self.__query = re.sub('MIRROR', self.mirror, self.__query)
        self.__query = re.sub('ARCHIVED', self.archived, self.__query)

        return self.__query

    @property
    def stars(self):
        if 'stars' in self.__yml.get('repositories'):
            if re.match(r'^(>=|=<|<|>|=>|<=)\s*\d+$', self.__yml['repositories']['stars']):
                return self.__yml['repositories']['stars']
            else:
                raise Exception('Invalid value for stars')
        else:
            return str(DEFAULT_STARS)
    
    @property
    def releases(self):
        if 'releases' in self.__yml.get('repositories'):
            if re.match(r'^(>=|=<|<|>|=>|<=)\s*\d+$', self.__yml['repositories']['releases']):
                return self.__yml['repositories']['releases']
            else:
                raise Exception('Invalid value for releases')
        else:
            return f'>{DEFAULT_RELEASES}'

    @property
    def mirror(self):
        if 'mirror' in self.__yml.get('repositories'):
            if self.__yml['repositories']['mirror'] in ('false', 'true', True, False):
                return str(self.__yml['repositories']['mirror']).lower()
            else:
                raise Exception('Invalid value for mirror') 
        else:
            return DEFAULT_MIRROR

    @property
    def archived(self):
        if 'mirror' in self.__yml.get('repositories'):
            if self.__yml['repositories']['archived'] in ('false', 'true', True, False):
                return str(self.__yml['repositories']['archived']).lower()
            else:
                raise Exception('Invalid value for archived') 
        else:
            return DEFAULT_ARCHIVED

    @property
    def date_from(self):
        year = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('year', '2014'))
        month = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('month', '11'))
        day = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('day', '27'))
        hh = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('hh', '00'))
        mm = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('mm', '00'))
        ss = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('ss', '00'))

        if not re.match('^\d{4}$', year.strip()):
            raise Exception('Invalid value for year')

        if not re.match('^\d{2}$', month.strip()):
            raise Exception('Invalid value for month')

        if not re.match('^\d{2}$', day.strip()):
            raise Exception('Invalid value for day')

        if not re.match('^\d{2}$', hh):
            raise Exception('Invalid value for hour')

        if not re.match('^\d{2}$', mm):
            raise Exception('Invalid value for minutes')

        if not re.match('^\d{2}$', ss):
            raise Exception('Invalid value for seconds')

        return f'{year}-{month}-{day}Z{hh}:{mm}:{ss}Z'

    @property
    def date_to(self):
        year = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('year', '2014'))
        month = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('month', '11'))
        day = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('day', '28'))
        hh = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('hh', '00'))
        mm = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('mm', '00'))
        ss = str(self.__yml.get('repositories', {}).get('created', {}).get('date_from', {}).get('ss', '00'))

        if not re.match('^\d{4}$', year.strip()):
            raise Exception('Invalid value for year')

        if not re.match('^\d{2}$', month.strip()):
            raise Exception('Invalid value for month')

        if not re.match('^\d{2}$', day.strip()):
            raise Exception('Invalid value for day')

        if not re.match('^\d{2}$', hh):
            raise Exception('Invalid value for hour')

        if not re.match('^\d{2}$', mm):
            raise Exception('Invalid value for minutes')

        if not re.match('^\d{2}$', ss):
            raise Exception('Invalid value for seconds')

        return f'{year}-{month}-{day}Z{hh}:{mm}:{ss}Z'

    @property
    def timespan(self):
        timespan = str(self.__yml.get('repositories', {}).get('created', {}).get('timespan', 24))

        if not re.match('^\d{2}$', timespan.strip()):
            raise Exception('Invalid value for timespan')

        return timespan