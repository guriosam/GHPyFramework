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
        The test here analyzes if each metric is generating a CSV in the end.
        In order to do that, we check if a list with the length of each CSV have the size of the input list of metrics.
        Total metrics = 11

        """
        project = 'test_collector'
        collector = MetricsCollector('', project)
        assert (len(collector.run_metrics()) == 11)

    def test_compile_data(self):
        """

        """
        project = 'test_collector'
        config = JSONHandler('../').open_json('config.json')
        collector = MetricsCollector(config['output_path'], project)
        assert(collector.compile_data() is not None)


metrics = TestMetricsCollector()
