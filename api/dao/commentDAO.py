from api.dao.dao_interface import DAOInterface

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class CommentDAO(DAOInterface):
	
	def __init__(self):
		self.id = -1
		self.body = ""
		self.path = ""
		self.created_at = ""
		self.updated_at = ""
		self.position = -1
		self.commit_id = ""
		self.line = -1
		self.issue_number = -1

	def read_from_json(self, comment : dict):
		"""
		Filters the GitHub API JSON to collect only the proposed fields.

		:param comment: json containing the comment object from the GitHub API
		:type comment: dict
		"""
		self.id = comment['id']
		if 'path' in comment.keys():
			self.path = comment['path']
		self.created_at = comment['created_at']
		self.updated_at = comment['updated_at']
		if 'position' in comment.keys():
			self.position = comment['position']
		if 'commit_id' in comment.keys():
			self.commit_id = comment['commit_id']
		if 'line' in comment.keys():
			self.line = comment['line']
		self.body = comment['body']
		issue_url = comment['issue_url'].split('/')
		self.issue_number = issue_url[len(issue_url) - 1]