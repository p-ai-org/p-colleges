import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scoreFunction import scoreFunction

class KMeansClusterer:
    """
    A class for clustering using kMeans and finding the optimal number of clusters
    """

    def __init__(self, embeddings, max_clusters):
        """
        Initializes the KMeansClusterer class with the given dataset and maxiumum number of clusters to test.

        Args:
            embeddings (dict): A dictionary of word or document embeddings.
            max_clusters (int): The maximum number of clusters to consider.
        """
        self.max_clusters = max_clusters
        self.dataset = pd.DataFrame.from_dict(embeddings,orient='index')
        self.clusterings = {}
        for n_clust in range(2,max_clusters+1):
            self.clusterings[n_clust] = self.cluster_data(n_clust)


    def cluster_data(self, n_clust):
        """
        Cluster the dataset using the specified metric and a range of cluster sizes.

        Args:
            n_clust (int): The number of clusters to use.

        Returns:
            cluster_labels (numpy.ndarray): The cluster labels assigned to each data point.
        """
        if n_clust in self.clusterings:
            return self.clusterings[n_clust]

        init_method = 'k-means++'
        n_clust = n_clust
        n_init = 100
        max_iter = 1000
        usetol = 1e-10
        verbose = 0
        random_state = 47
        algorithm = "auto"

        sk_KMeans = KMeans(n_clusters = n_clust,
                           init = init_method,
                           n_init = n_init,
                           max_iter = max_iter,
                           tol = usetol,
                           verbose = verbose,
                           random_state = random_state,
                           algorithm = algorithm)

        return sk_KMeans.fit(self.dataset)



    def evaluate_clustering(self, metric="si",sf_weight=1):
        """
        Create a graph showing how the chosen metric varies with the number of clusters.

        Args:
            metric (str): The clustering metric to use (e.g. 'si' for silhoute score or 'sf for score function).
            sf_weight (int): The weight to use to adjust the score function to avoid overflow
        """
        scores = []
        for k in range(2, self.max_clusters + 1):
            # Cluster the data for each value of k
            if metric == "si":
                score = silhouette_score(self.dataset, self.clusterings[k].labels_)
                scores.append(score)
            elif metric == "sf":
                score = scoreFunction(self.dataset,self.clusterings[k], sf_weight)
                scores.append(score)

        # Plot the scores vs. the number of clusters
        plt.plot(range(2, self.max_clusters + 1), scores, marker='o')
        plt.xlabel('Number of Clusters')
        if metric == "si":
            plt.ylabel('Silhouette Score')
            plt.title('Silhouette Score vs. Number of Clusters')
        elif metric == "sf":
            plt.ylabel('SF Score')
            plt.title('SF Score vs. Number of Clusters')
        plt.show()

    def get_labled_cluster(self, n_clust):
        """
        Returns a dictionary of clustered words or documents based on the number of clusters specified.

        Args:
            n_clust (int): The number of clusters to use.

        Returns:
            clustered (dict): A dictionary of clusters where the keys are 0 through n_clust - 1 and the values are lists of words belonging to that cluster.
        """
        clustered = {}
        for word, clust_id in zip(self.dataset.index[:], self.clusterings[n_clust].labels_):
            if clust_id in clustered:
                clustered[clust_id].append(word)
            else:
                clustered[clust_id] = [word]
        return clustered