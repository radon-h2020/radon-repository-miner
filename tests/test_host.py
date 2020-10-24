import unittest
import os


from radonminer.hosts import GithubHost, GitlabHost


class HostTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.gh = GithubHost(full_name='stefanodallapalma/test-github-apis')

        cls.gl = GitlabHost(full_name='stefanodallapalma/test-gitlab-apis')

    def test_github_get_labels(self):
        assert set(self.gh.get_labels()) == {'bug', 'documentation', 'duplicate', 'duplicate', 'enhancement',
                                             'good first issue', 'help wanted', 'invalid', 'question', 'wontfix'}

    def test_github_get_closed_issues(self):
        assert len(self.gh.get_closed_issues('bug')) == 1
        assert self.gh.get_closed_issues('bug')[0].number == 2

    def test_github_get_commit_closing_issue(self):
        issues = self.gh.get_closed_issues('bug')
        issue = [issue for issue in issues if issue.number == 2][0]
        closing_commit = self.gh.get_commit_closing_issue(issue)
        assert closing_commit == 'c9ada15de53d048f4d8e74d12bea62174bc0f957'

    def test_gitlab_get_labels(self):
        assert self.gl.get_labels() == {'bug', 'confirmed', 'critical', 'discussion', 'documentation', 'enhancement',
                                        'suggestion', 'support'}

    def test_gitlab_get_closed_issues(self):
        assert len(self.gl.get_closed_issues('bug')) == 1
        assert self.gl.get_closed_issues('bug')[0].iid == 2

    def test_gitlab_get_commit_closing_issue(self):
        issues = self.gl.get_closed_issues('bug')
        issue = [issue for issue in issues if issue.iid == 2][0]
        closing_commit = self.gl.get_commit_closing_issue(issue)
        assert closing_commit == '6aa96ed603f827f0bef9f9553b39c3234d1c119f'


if __name__ == '__main__':
    unittest.main()
