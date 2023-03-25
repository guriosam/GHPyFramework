import matplotlib.pyplot as plt
import networkx as nx

class SocialNetwork:

    def __init__(self, database):
        self.graph = nx.Graph()
        self.database = database
        self.construct_graph()

        self.lcc = self.largest_connected_component()

    @staticmethod
    def _get_merged_by(pull):

        if pull['merged_by']:
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
            commentators.add(comment['user']['login'])

        return commentators

    def construct_graph(self):

        pulls_database = self.database['pull_requests']
        comments_database = self.database['comments']

        pulls = pulls_database.find().sort({'created_at': 1})

        for pull in pulls:

            pull_author = pull['author']['login']

            pull_comments = comments_database.find({'issue_number': pull['number']})

            merged_by = self._get_merged_by(pull)
            if merged_by:
                merged_by = {merged_by}
            else:
                merged_by = {}

            assignees = self._get_assignees(pull)
            reviewers = self._get_reviewers(pull)

            commentators = self._get_commentators(pull_comments)

            all_users = set()

            all_users.update(merged_by, reviewers, assignees, commentators)
            if pull_author in all_users:
                all_users.remove(pull_author)

            all_users = list(all_users)

            for participant in all_users:
                try:
                    self.graph[pull_author][participant]['weight'] += 1
                except (KeyError, IndexError):
                    self.graph.add_edge(pull_author, participant, weight=1)

    def show_graph(self):
        nx.draw(self.graph)
        plt.show()

    def largest_connected_component(self):
        try:
            return max(nx.connected_component_subgraphs(self.graph), key=len)
        except:
            return self.graph

    def degree_centrality(self):
        nodes_dict = nx.degree_centrality(self.lcc)
        try:
            return nodes_dict[self.revision_author]
        except KeyError:
            return 0

    def closeness_centrality(self):
        try:
            return nx.closeness_centrality(self.lcc, u=self.revision_author)
        except nx.exception.NodeNotFound:
            return 0

    def betweenness_centrality(self):
        nodes_dict = nx.betweenness_centrality(self.lcc, weight='weight')
        try:
            return nodes_dict[self.revision_author]
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
            return nodes_dict[self.revision_author]
        except KeyError:
            return 0

    def clustering_coefficient(self):
        try:
            return nx.clustering(self.lcc, nodes=self.revision_author, weight='weight')
        except nx.exception.NetworkXError:
            return 0

    def k_coreness(self):
        nodes_dict = nx.core_number(self.lcc)
        try:
            return nodes_dict[self.revision_author]
        except KeyError:
            return 0