from api.dao.dao_interface import DAOInterface

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class LabelDAO(DAOInterface):

    def __init__(self):
        self.id = -1
        self.name = ""
        self.description = ""
        self.color = ""
        self.default = True

    def read_from_json(self, label: dict):
        """
        Filters the GitHub API JSON to collect only the proposed fields.

        :param label: json containing the label object from the GitHub API
        :type label: dict
        """
        self.id = label['id']
        self.name = label['name']
        if 'description' in label.keys():
            self.description = label['description']
        self.color = label['color']
        self.default = label['default']
