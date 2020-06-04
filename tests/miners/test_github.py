import os
import pytest

from datetime import datetime

from iacminer.miners.github import GithubMiner

from dotenv import load_dotenv

load_dotenv()

TEST_DATA = [
    (datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-01-03', '%Y-%m-%d'),
     datetime.strptime('2019-01-01', '%Y-%m-%d'), 0, 1000, 0, False, None, 2),
    (datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-01-03', '%Y-%m-%d'),
     datetime.strptime('2019-01-01', '%Y-%m-%d'), 0, 1000, 0, True, None, 2),
    (datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-01-03', '%Y-%m-%d'),
     datetime.strptime('2019-01-01', '%Y-%m-%d'), 0, 1000, 0, False, 'TypeScript', 1),
    (datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-01-03', '%Y-%m-%d'),
     datetime.strptime('2020-01-20', '%Y-%m-%d'), 0, 1000, 0, False, None, 2),
    (datetime.strptime('2020-01-01', '%Y-%m-%d'), datetime.strptime('2020-01-03', '%Y-%m-%d'),
     datetime.strptime('2020-01-20', '%Y-%m-%d'), 0, 1000, 0, False, 'TypeScript', 1)
]

@pytest.mark.parametrize(
    'date_from, date_to, pushed_after, min_releases, min_stars, min_watchers, include_fork, primary_language, '
    'expected_len',
    TEST_DATA)
def test(date_from, date_to, pushed_after, min_releases, min_stars, min_watchers, include_fork, primary_language,
         expected_len):
    miner = GithubMiner(
        access_token=os.getenv('GITHUB_ACCESS_TOKEN'),
        date_from=date_from,
        date_to=date_to,
        pushed_after=pushed_after,
        min_stars=min_stars,
        min_releases=min_releases,
        min_watchers=min_watchers,
        primary_language=primary_language,
        include_fork=include_fork
    )

    date_from = date_from.strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to = date_to.strftime('%Y-%m-%dT%H:%M:%SZ')
    pushed_after = pushed_after.strftime('%Y-%m-%dT%H:%M:%SZ') if pushed_after else ''

    repos = list(miner.mine())
    assert repos
    assert len(repos) == expected_len

    for repo in repos:
        assert repo['id']
        assert repo['default_branch']
        assert repo['owner']
        assert repo['name']
        assert repo['issues'] > 0
        assert repo['releases'] >= min_releases
        assert repo['stars'] >= min_stars
        assert repo['watchers'] >= min_watchers
        assert repo['primary_language'].lower() == primary_language.lower() if primary_language else True
        assert date_from <= repo['created_at'] <= date_to
        assert repo['pushed_at'] >= pushed_after
