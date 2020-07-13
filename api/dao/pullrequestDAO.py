from api.dao.dao_interface import DAOInterface
from api.dao.labelDAO import LabelDAO

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class PullRequestDAO(DAOInterface):
	
	def __init__(self):
		self.id = -1
		self.pull_request_number = -1
		self.state = ""
		self.title = ""
		self.body = ""
		self.locked = False
		self.user = ''
		self.labels = []
		self.assignees = []
		self.requested_reviewers = [] 
		self.merged_sha = ""
		self.comments = 0
		self.created_at = ""
		self.updated_at = ""
		self.closed_at = ""
		self.merged_at = ""
		self.author_association = ""
		self.merged = False
		self.merged_by = ''
		self.review_comments = 0
		self.commits = 0
		self.additions = 0
		self.deletions = 0
		self.changed_files = 0

	def read_from_json(self, pull : dict):
		"""
		Filters the GitHub API JSON to collect only the proposed fields.

		:param pull: json containing the pull request object from the GitHub API
		:type pull: dict
		"""
		self.id = pull['id']
		self.pull_request_number = pull['number']
		self.state = pull['state']
		self.title = pull['title']
		self.body = pull['body']
		self.locked = pull['locked']

		if pull['user']:
			self.user = pull['user']['login']

		if 'labels' in pull.keys():
			if pull['labels']:
				self.labels = []
				for labelJSON in pull['labels']:
					label = LabelDAO()
					label.read_from_json(labelJSON)
					self.labels.append(label.__dict__)

		if pull['requested_reviewers']:
			self.requested_reviewers = []
			for userJSON in pull['requested_reviewers']:
				self.requested_reviewers.append(userJSON['login'])

		if pull['assignees']:
			self.assignees = []
			for userJSON in pull['assignees']:
				self.assignees.append(userJSON['login'])

		self.comments = pull['comments']
		self.commits = pull['commits']
		self.additions = pull['additions']
		self.deletions = pull['deletions']
		self.changed_files = pull['changed_files']
		self.review_comments = pull['review_comments']
		self.created_at = pull['created_at']
		self.updated_at = pull['updated_at']
		self.closed_at = pull['closed_at']
		self.merged_at = pull['merged_at']
		self.merged = pull['merged']
		self.author_association = pull['author_association']

		if pull['merged_by']:
			self.merged_by = pull['merged_by']['login']