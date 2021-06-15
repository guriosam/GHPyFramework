import os
import json


class JSONHandler:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.path):
            os.makedirs(self.path)


    def save_json(self, data, name):
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        except OSError:
            print ("Creation of the directory %s failed" % self.path)
        with open(self.path + name + '.json', 'w') as outfile:
            json.dump(data, outfile, indent = 4)
            print(self.path + name + ' has been saved.')

    def open_json(self, name):
        try:
            if not os.path.exists(self.path + name):
                print(self.path + name)
                return {}
            with open(self.path + name, encoding='utf-8', errors='ignore') as json_file:
                data = json.load(json_file)
                return data
        except Exception as e:
            print(e)
            print(self.path + name)
            return {}

    @staticmethod
    def file_exists(path):
        try:
            return os.path.exists(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        return False