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
        print('Testing collect issues')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_issues(owner, project)) == 2)


    def test_collect_pulls(self):
        print('Testing collect pulls')
        self.collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(
            self.collector.collect_all(project, PullsAPI(owner, project), 'pulls', 'number', PullRequestDAO())) == 1)

    def test_collect_commits(self):
        print('Testing collect commits')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_commits(owner, project)) == 2)

    def test_collect_comments(self):
        print('Collecting Issues Comments')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'
        assert (len(collector.collect_all(project, CommentAPI(owner, project), 'comments/issues/', 'issue_url',
                                          CommentDAO())) == 4)

    def test_collect_events(self):
        print('Testing collect events')
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(collector.collect_events(owner, project)) == 2)

    def test_collect_all(self):
        print('Testing collect all')

        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(
            collector.collect_all(project, IssueAPI(owner, project), 'issues', 'number', IssueDAO())) == 2)

    def test_collect_commits_on_pulls(self):
        collector = APICollector()
        owner = 'guriosam'
        project = 'test_collector'

        assert (len(collector.collect_commits_on_pulls(owner, project)) == 1)


test = TestAPICollector()
# test.test_collect_issues('guriosam', 'test_collector')
