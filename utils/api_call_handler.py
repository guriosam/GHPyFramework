from pip._vendor import requests

from utils.json_handler import JSONHandler


class APICallHandler:

    def __init__(self):
        self.position = 0
        self.config = JSONHandler('./').open_json('config.json')
        self.tokens_len = len(self.config['tokens'])
        self.username = self.config['tokens'][self.position]['username']
        self.auth_token = self.config['tokens'][self.position]['token']

    def request(self, request_url):

        retry = 1
        while True:
            try:
                request = requests.get(request_url, params=[], auth=(self.username, self.auth_token))

                if request.status_code == 200:
                    break
                elif request.status_code == 403:
                    self.position = self.position + 1
                    if self.position == self.tokens_len:
                        self.position = 0
                else:
                    if 'page' in request_url:
                        print(request.status_code)
                        print(request_url)
                        return []
                    else:
                        print(request.status_code)
                        print(request_url)
                        return {}

            except Exception as e:
                print('Error in: ' + request_url)
                print('Retry number ' + str(retry))
                print(e)
                retry = retry + 1

        return request.json()