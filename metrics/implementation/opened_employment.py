from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class OpenedByEmployeeOrTemporary:

    def __init__(self, project):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']

    def opened_employee_or_temporary(self):
        """
        Collect the status of the user that opened the issue/pull request. Employee if has an author_association OWNER, MEMBER, COLLABORATOR or CONTRIBUTOR. Temporary else.
        :return: list of the status of the user that opened the issue/pull request by issue/pull request
        :rtype: list
        """
        print("#### Opened by Employee or Temporary ####")

        path = self.path + '/' + self.project
        json = JSONHandler(path + '/')
        issues = json.open_json(self.project + '_issues.json')
        pulls = json.open_json(self.project + '_pulls.json')

        opened_by = [['number', 'status', 'user']]
        for issue in issues:
            if 'author_association' in issue.keys():
                # print(issue['author_association'])
                opened_by.append(
                    [issue['issue_number'], self._employee_or_temporary(issue['author_association']), issue['user']])

        for pull in pulls:
            if 'author_association' in pull.keys():
                opened_by.append(
                    [pull['pull_request_number'], self._employee_or_temporary(pull['author_association']),
                     pull['user']])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_opened_by.csv',
                      opened_by)

        return opened_by

    def _employee_or_temporary(self, association: str):
        """
        Checks if a association tags belongs to Employee or Temporary category
        :param association: author_association of an user
        :return: user status: Employee or Temporary
        :rtype: str
        """
        if 'OWNER' in association:
            return 'employee'

        if 'MEMBER' in association:
            return 'employee'

        if 'COLLABORATOR' in association:
            return 'employee'

        if 'CONTRIBUTOR' in association:
            return 'employee'

        return 'temporary'
