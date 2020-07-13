from api.dao.dao_interface import DAOInterface
from api.dao.fileCommitDAO import FileDAO

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class CommitDAO(DAOInterface):
	
	def __init__(self):
		self.author_login = ""
		self.author_name = ""
		self.author_date = ""
		self.author_email = ""
		self.committer_login = ""
		self.committer_name = ""
		self.committer_date = ""
		self.committer_email = ""
		self.commit_sha = ""	
		self.additions = 0
		self.deletions = 0
		self.changed_files = 0
		self.message = ""
		self.files = []

	def read_from_json(self, commit: dict):
		"""
		Filters the GitHub API JSON to collect only the proposed fields.

		:param commit: json containing the commit object from the GitHub API
		:type commit: dict
		"""
		if commit['author']:
			self.author_login = commit['author']['login']
		self.author_name = commit['commit']['author']['name']
		self.author_date = commit['commit']['author']['date']
		self.author_email = commit['commit']['author']['email']

		if commit['committer']:
			self.committer_login = commit['committer']['login']
		self.committer_name = commit['commit']['committer']['name']
		self.committer_date = commit['commit']['committer']['date']
		self.committer_email = commit['commit']['committer']['email']
		self.commit_sha = commit['sha']
		self.additions = commit['stats']['additions']
		self.deletions = commit['stats']['deletions']
		self.changed_files = commit['stats']['total']
		self.message = commit['commit']['message']
		
		if commit['files']:
			for file in commit['files']:
				fileDAO = FileDAO()
				fileDAO.read_from_json(file)
				self.files.append(fileDAO.__dict__)
