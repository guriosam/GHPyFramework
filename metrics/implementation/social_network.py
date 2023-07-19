import matplotlib.pyplot as plt
import networkx as nx
from pymongo.database import Database


class SocialNetwork:

    def __init__(self, pull: None, database: Database = None):
        self.graph = nx.Graph()
        self.database = database
        self.pull_target = pull
        self.construct_graph()

        self.lcc = self.largest_connected_component()

    @staticmethod
    def _get_pull_author(pull):
        if pull['user']['login']:
            pull_author = pull['user']['login']
            return pull_author

        return None

    @staticmethod
    def _get_merged_by(pull):
        if pull['merged_by'] and pull['merged_by']['type'] != "Bot":
            user_login = pull['merged_by']['login']
            return user_login

        return None

    @staticmethod
    def _get_assignees(pull):

        assignees = set()
        if pull['assignees']:
            for assignee in pull['assignees']:
                user_login = assignee['login']
                assignees.add(user_login)

        return assignees

    @staticmethod
    def _get_reviewers(pull):

        reviewers = set()

        if pull['requested_reviewers']:
            for reviewer in pull['requested_reviewers']:
                user_login = reviewer['login']
                reviewers.add(user_login)

        return reviewers

    @staticmethod
    def _get_commentators(comments):
        commentators = set()
        for comment in comments:
            if comment['user']['type'] == "Bot":
                continue
            commentators.add(comment['user']['login'])
        return commentators

    def get_pull_requests(self):
        pull_target_merged_at = self.pull_target['merged_at']
        print(pull_target_merged_at)
        pulls = self.database['pull_requests'].aggregate([
            {"$match": {
                "merged": True,
                "merged_at": {"$lte": pull_target_merged_at}
            }},
            {"$group": {
                "_id": "$number",  # Group by "number"
                "doc": {"$first": "$$ROOT"}  # Keep the first document of each group
            }},
            {"$replaceRoot": {"newRoot": "$doc"}},  # Replace the root of each document with the "doc" field
            {"$sort": {"merged_at": 1}}
        ])

        return pulls

    def construct_graph(self):

        pulls = self.get_pull_requests()
        # TODO verficar a ordem cronologia para o pull request de referencia

        pull_target_author = self._get_pull_author(self.pull_target)
        print(pull_target_author)

        for pull in pulls:
            # print(pull["number"])
            # print(self.pull_target["number"])

            # TODO check de o numero do pull request corrent eh diferent do referencia

            pull_author = self._get_pull_author(pull)
            if pull_author:
                pull_author = {pull_author}
            else:
                pull_author = {}

            pull_comments = self.database['comments'].find({'issue_number': pull['number']})

            merged_by = self._get_merged_by(pull)
            if merged_by:
                merged_by = {merged_by}
            else:
                merged_by = {}

            assignees = self._get_assignees(pull)
            reviewers = self._get_reviewers(pull)

            commentators = self._get_commentators(pull_comments)
            all_users = set()
            all_users.update(merged_by, reviewers, assignees, commentators, pull_author)
            if pull_target_author in all_users:
                all_users.remove(pull_target_author)

            all_users = list(all_users)
            for participant in all_users:
                if participant == pull_target_author:
                    continue

                try:
                    self.graph[pull_target_author][participant]['weight'] += 1
                except (KeyError, IndexError):
                    self.graph.add_edge(pull_target_author, participant, weight=1)

            # if pull['number'] == self.pull_target['number']:
            #     continue

    def show_graph(self):
        print(nx.draw(self.graph))

    def largest_connected_component(self):
        try:
            return max(nx.connected_component_subgraphs(self.graph), key=len)
        except:
            return self.graph

    def degree_centrality(self):
        nodes_dict = nx.degree_centrality(self.lcc)
        try:
            return nodes_dict[self._get_pull_author(self.pull_target)]
        except KeyError:
            return 0

    def closeness_centrality(self):
        try:
            return nx.closeness_centrality(self.lcc, u=self._get_pull_author(self.pull_target))
        except nx.exception.NodeNotFound:
            return 0

    def betweenness_centrality(self):
        nodes_dict = nx.betweenness_centrality(self.lcc, weight='weight')
        try:
            return nodes_dict[self._get_pull_author(self.pull_target)]
        except KeyError:
            return 0

    def eigenvector_centrality(self):
        try:
            nodes_dict = nx.eigenvector_centrality_numpy(self.lcc)
        except:
            try:
                nodes_dict = nx.eigenvector_centrality(self.lcc)
            except:
                return 0
        try:
            return nodes_dict[self._get_pull_author(self.pull_target)]
        except KeyError:
            return 0

    def clustering_coefficient(self):
        try:
            return nx.clustering(self.lcc, nodes=self._get_pull_author(self.pull_target), weight='weight')
        except nx.exception.NetworkXError:
            return 0

    def k_coreness(self):
        nodes_dict = nx.core_number(self.lcc)
        try:
            return nodes_dict[self._get_pull_author(self.pull_target)]
        except KeyError:
            return 0
