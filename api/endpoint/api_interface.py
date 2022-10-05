"""
Interface for classes responsible for collecting the data from the GitHub API
"""

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class APIInterface(object):

    def collect_batch(self, review: bool = False, save: bool = True):
        pass

    def collect_single(self, parameter: str):
        pass
