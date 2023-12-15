import csv
import subprocess
import os
import time
import sys

UNDERSTAND_PATH = 'C:/Users/Caio/research/SciTools/bin/pc-win64/und.exe'

#try:
import pydriller
#except ModuleNotFoundError:
    #python = sys.executable
    #subprocess.check_call([python, '-m', 'pip3', 'install', 'pydriller'], stdout=subprocess.DEVNULL)


class Checkout:

    def __init__(self, path, project_name, language):
        self.gr = pydriller.Git(path)
        self.commits = []
        self.language = language
        self.path = path
        self.project_name = project_name
        self.script_path = 'C:/Users/Caio/PycharmProjects/understand'

    def check(self, chash):
        if os.path.exists(self.path + '/und_' + chash + '.und/'):
            #print("Commit", chash, "already collected, skipping...")
            return True
        else:
            print("Commit", chash, "not found, collecting...")
            return False

    def _get_commit_list(self):
        with open(self.script_path + '/buggy/' + self.project_name + '.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1

                self.commits.append(row['commit'])
                line_count += 1

    def checkout(self):
        self._get_commit_list()

        for commit in self.commits:
            if self.check(commit):
                continue

            print("git checkout on commit", commit + "...")
            self.gr.checkout(commit)

            return


if __name__ == '__main__':
    args = sys.argv
    Checkout(path=args[1], project_name=args[2], language=args[3]).checkout()
