import csv
import os


class CSVHandler:

    def open_csv(self, path):
        csv_file = []
        with open(path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                csv_file.append(row)
        return csv_file

    def write_csv(self, path, name, lines):
        if not os.path.exists(path):
            os.makedirs(path)
        f = open(path + name, 'w', newline='', encoding="utf-8")
        with f:
            writer = csv.writer(f)
            for row in lines:
                if row:
                    writer.writerow(row)

    def open_csv_as_dict(self, path, all_row=False):

        if not os.path.exists(path):
            print('File does not exists: ' + path)
            return {}


        lines = self.open_csv(path)
        lines2 = self.open_csv(path)

        dict = {}

        csv = iter(lines)
        csv2 = iter(lines2)

        next(csv)
        next(csv2)

        flag = False
        aux = {}
        for line in csv2:
            if line[0] not in aux.keys():
                aux[line[0]] = ''
            else:
                flag = True

        if all_row:
            for line in csv:
                dict[line[0]] = line[1:]

            return dict

        for line in csv:
            if flag:
                if line[0] not in dict.keys():
                    dict[line[0]] = []
                dict[line[0]].append(line[1])
            else:
                dict[line[0]] = line[1]

        return dict
