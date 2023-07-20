import json
import os
import sys
from os import listdir
from os.path import isfile, join
from pymongo.database import Database

from metrics.implementation.social_network import SocialNetwork


class CollaborationNetworks:

    def __init__(self, owner: str, repo: str, database: Database = None):
        self.owner = owner
        self.repo = repo
        self.database = database

    def get_social_network(self, pull):
        social_network = SocialNetwork(pull, self.database)
        return social_network

    def get_collaboration_networks_metrics(self):
        pulls_requests = self.database['pull_requests']
        pulls = pulls_requests.aggregate([
            {"$match": {"merged": True}},  # Filter the documents where "merged" is True
            {"$sort": {"merged_at": 1}} # Sort the documents by "merged_at" in ascending order
        ])

        all_collaboration_networks = {}

        for pull in pulls:

            social_network = self.get_social_network(pull)
            print(social_network.graph)

            collaboration_networks = {
                'social_degree': self.get_social_degree(social_network),
                'social_closeness': self.get_social_closeness(social_network),
                'social_betweenness': self.get_social_betweenness(social_network),
                'social_eigenvector': self.get_social_eigenvector(social_network),
                'social_clustering': self.get_social_clustering(social_network),
                'social_k_coreness': self.get_social_k_coreness(social_network),
            }
            self.database['metrics'].update_one({"issue_number": pull['number']},
                                    {'$set': {"collaboration_networks": [collaboration_networks]}})

            print(pull['number'])
            print(collaboration_networks)
            all_collaboration_networks[pull['number']] = collaboration_networks

        return all_collaboration_networks

    def get_social_degree(self, social_network):
        social_degree = round(social_network.degree_centrality(), 4) 
        return social_degree

    def get_social_closeness(self, social_network):
        social_closeness = round(social_network.closeness_centrality(), 4)
        return social_closeness

    def get_social_betweenness(self, social_network):
        social_betweenness = round(social_network.betweenness_centrality(), 4)
        return social_betweenness

    def get_social_eigenvector(self, social_network):
        social_eigenvector = round(social_network.eigenvector_centrality(), 4)
        return social_eigenvector

    def get_social_clustering(self, social_network):
        social_clustering = round(social_network.clustering_coefficient(), 4)
        return social_clustering

    def get_social_k_coreness(self, social_network):
        social_k_coreness = round(social_network.k_coreness(), 4)
        return social_k_coreness
