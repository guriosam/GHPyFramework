"""
Interface for the Data Access Objects of the GitHub API JSONs.
"""

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class DAOInterface:

    def read_from_json(self, object_type : dict):
        pass