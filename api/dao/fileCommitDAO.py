from api.dao.dao_interface import DAOInterface

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class FileDAO(DAOInterface):

    def __init__(self):
        self.sha = ''
        self.filename = ''
        self.status = ''
        self.additions = 0
        self.deletions = 0
        self.changes = 0
        self.patch = ''

    def read_from_json(self, file: dict):
        self.sha = file['sha']
        self.filename = file['filename']
        self.status = file['status']
        self.additions = file['additions']
        self.deletions = file['deletions']
        self.changes = file['changes']
        if 'patch' in file.keys():
            self.patch = file['patch']
