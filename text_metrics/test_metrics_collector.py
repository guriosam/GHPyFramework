#!/usr/bin/env python
"""
Tests the methods of MetricsCollector class
"""

from metrics.metrics_collector import MetricsCollector
import unittest

from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"


class TestMetricsCollector(unittest.TestCase):

    def test_run_metrics(self):
        """
        Tests the run_metrics function of the MetricsCollector class
        First test here analyzes if each metric is generating a CSV in the end.
        In order to do that, we check if a list with the length of each CSV have the size of the input list of metrics.
        Total metrics = 11
        Second test analyzes if the length of the 'number of users' metric is 3.
        Third test analyzes if the length of the 'discussion length' metric is 1.
        """
        project = 'test_collector'
        collector = MetricsCollector('', project)
        assert (len(collector.run_metrics()) == 11)
        assert (collector.run_metrics()[0] == 3)
        assert (collector.run_metrics()[10] == 1)

    def test_compile_data(self):
        """
        Tests the compile_data function of the MetricsCollector class
        First test analyzes if the CSV returned is not NULL
        Second test analyzes if the length in lines of the CSV is equal to three (header plus two rows)
        Third test analyzes if the identifier of the second row is 1, since is the identifier of the first issue.
        """
        project = 'test_collector'
        config = JSONHandler('../').open_json('config.json')
        collector = MetricsCollector(config['output_path'], project)
        assert (collector.compile_data() is not None)
        assert (len(collector.compile_data()) == 3)
        assert (collector.compile_data()[1][0] == '1')


metrics = TestMetricsCollector()
