from os import listdir
from os.path import isfile, join

from utils.csv_handler import CSVHandler
from utils.json_handler import JSONHandler

__author__ = "Caio Barbosa"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Caio Barbosa"
__email__ = "csilva@inf.puc-rio.br"
__status__ = "Production"

class NumberSnippets:

    def __init__(self, project: str):
        config = JSONHandler('../').open_json('config.json')
        self.project = project
        self.path = config['output_path']
        self.patches_size = {}

    def get_number_of_patches(self):
        """
        Collects the number of snippets inside each comment of issues and pull requests.

        :return: list of the number of snippets per issue or pull request
        :rtype: list
        """
        print('#### Number of Snippets ####')

        mypath = self.path + self.project + '/comments/individual/'
        json = JSONHandler(mypath)

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        patches_in_discussion = {}
        for file in onlyfiles:
            comments = json.open_json(file)
            for comment in comments:
                if 'issue_url' in comment.keys():
                    issue = comment['issue_url'].split('/')
                    issue = issue[len(issue) - 1]

                    if issue not in patches_in_discussion.keys():
                        patches_in_discussion[issue] = 0

                    if '```' in comment['body']:
                        patches = comment['body'].split('```')
                        count = 0
                        aux = 0
                        if issue not in self.patches_size.keys():
                            self.patches_size[issue] = 0
                        for patch in patches:

                            if len(patches) != 1:
                                aux += 1
                                if aux%2 != 0:
                                    continue

                            self.patches_size[issue] += len(patch)

                            count += 1
                        patches_in_discussion[issue] += count


        number_of_patches_in_discussion = [['issue', 'number_patches']]

        for key in patches_in_discussion.keys():
            number_of_patches_in_discussion.append([key, patches_in_discussion[key]])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_patches_in_discussion.csv',
                      number_of_patches_in_discussion)

        return number_of_patches_in_discussion

    def get_patch_size(self):
        """
        Collects the size of the snippets of each comment in issues and pull requests.

        :return: list with the sizes of the patches per issue and pull request
        :rtype: list
        """
        print('#### Snippets Size ####')

        size_of_patches_in_discussion = [['issue', 'size_patches']]

        for key in self.patches_size.keys():
            #print(str(key) + ': ' + str(self.patches_size[key]))
            size_of_patches_in_discussion.append([key, self.patches_size[key]])

        csv = CSVHandler()
        csv.write_csv(self.path + '/' + self.project + '/metrics/',
                      self.project + '_patches_size_in_discussion.csv',
                      size_of_patches_in_discussion)

        return size_of_patches_in_discussion