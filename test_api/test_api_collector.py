#!/usr/bin/env python
"""
Tests the methods of APICollector class
"""

import unittest

from api.api_collector import APICollector
from api.dao.commentDAO import CommentDAO
from api.dao.issueDAO import IssueDAO
from api.dao.pullrequestDAO import PullRequestDAO
from api.endpoint.comment import CommentAPI
from api.endpoint.issue import IssueAPI
from api.endpoint.pullrequest import PullsAPI

__author__ = "Caio Barbosa"

__license__ = "GPL 3"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class TestAPICollector(unittest.TestCase):

    def test_collect_issues(self):
        """
        Testing the function collect_issues from APICollector class
        First test case sees if the list returned has size two, since there are just two issues on the repository (one issue and one pull request)
        Second test case sees if the ID of the first issue is 655043526, since this is the ID returned for the last issue of the repository
        """
        print('Testing collect issues')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_issues(owner, project)) == 2)
        assert (collector.collect_issues(owner, project)[0]['id'] == 655043526)

    def test_collect_pulls(self):
        """
        Testing the function collect_pulls from APICollector class
        First test case sees if the list returned has size one, since there are just one pull request on the repository
        Second test case sees if the ID of the first issue is 447649974, since this is the ID returned for the pull request on the repository
        """
        print('Testing collect pulls')
        self.collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(
            self.collector.collect_all(project, PullsAPI(owner, project), 'pulls', 'number', PullRequestDAO())) == 1)

        assert (self.collector.collect_all(project, PullsAPI(owner, project), 'pulls', 'number', PullRequestDAO())[0][
                    'id'] == 447649974)

    def test_collect_commits(self):
        """
        Testing the function collect_commits from APICollector class
        First test case sees if the list returned has size two, since there are just two commits on the repository
        Second test case sees if the hash of the first commit is 0263e46b9e4e6a50bf488de1024b3e4b5bf121e6, since this is the hash returned for the last commit of the repository
        """
        print('Testing collect commits')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_commits(owner, project)) == 2)
        assert (collector.collect_commits(owner, project)[0][
                    'commit_sha'] in '0263e46b9e4e6a50bf488de1024b3e4b5bf121e6')

    def test_collect_comments(self):
        """
        Testing the function collect_comments from APICollector class
        First test case sees if the list returned has size four, since there are just four comments on the repository
        Second test case sees if the ID of the first comment is 656896695, since this is the ID returned for the last comment of the repository
        """
        print('Collecting Issues Comments')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_all(project, CommentAPI(owner, project), 'comments/issues/', 'issue_url',
                                          CommentDAO())) == 4)
        assert (collector.collect_all(project, CommentAPI(owner, project), 'comments/issues/', 'issue_url',
                                      CommentDAO())[0]['id'] == 656896695)

    def test_collect_events(self):
        """
        Testing the function collect_events from APICollector class
        First test case sees if the list returned has size two, since there are just two events on the repository
        Second test case sees if the ID of the first event is 3536068866, since this is the ID returned for the last event of the repository
        """
        print('Testing collect events')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(collector.collect_events(owner, project)) == 2)
        assert (collector.collect_events(owner, project)[0]['id'] == 3536068866)

    def test_collect_all(self):
        """
        Testing the function collect_all from APICollector class
        The test case checks if the list returned has size equals to two.
        """
        print('Testing collect all')

        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(
            collector.collect_all(project, IssueAPI(owner, project), 'issues', 'number', IssueDAO())) == 2)

    def test_collect_commits_on_pulls(self):
        """
        Testing the function collect_commits_on_pulls from APICollector class
        First test case sees if the list returned has size one, since there is only one commit of pull requests
        Second test case sees if the hash of the first commit is 18f2864b807dc50208b3f49d9319ac1260499666, since this is the hash returned for the last commit of the repository
        """
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(collector.collect_commits_on_pulls(owner, project)) == 1)
        assert (collector.collect_commits_on_pulls(owner, project)[0] in '18f2864b807dc50208b3f49d9319ac1260499666')


test = TestAPICollector()
