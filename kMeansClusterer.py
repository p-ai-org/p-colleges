import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class KMeansClusterer:
    """
    A class for clustering using kMeans and finding the optimal number of clusters
    """

    def __init__(self, dataset, max_clusters):
        """
        Initializes the KMeansClusterer class with the given dataset and maxiumum number of clusters to test.

        Args:
            dataset (pandas.DataFrame): The dataset to be clustered. Each row should be an observation and each column should be a feature
            max_clusters (int): The maximum number of clusters to consider.
        """
        self.dataset = dataset
        self.metric = metric
        self.clusterings = {}
        for n_clust in range(2,max_clusters+1):
            self.clusterings[n_clust] = self.__cluster_data(n_clust)


    def __cluster_data(self, n_clust):
        """
        Cluster the dataset using the specified metric and a range of cluster sizes.

        Args:
            n_clust (int): The number of clusters to use.

        Returns:
            cluster_labels (numpy.ndarray): The cluster labels assigned to each data point.
        """

        init_method = 'k-means++'
        n_clust = n_clust
        n_init = 100
        max_iter = 1000
        usetol = 1e-10
        verbose = 0
        random_state = rand_state
        algorithm = "lloyd"

        sk_KMeans = KMeans(n_clusters = n_clust,
                           init = init_method,
                           n_init = n_init,
                           max_iter = max_iter,
                           tol = usetol,
                           verbose = verbose,
                           random_state = random_state,
                           algorithm = algorithm)

        return sk_KMeans.fit(dataset)



    def visualize_clusters(self, metric):
        """
        Create a graph showing how the chosen metric varies with the number of clusters.

        Args:
            metric (str): The clustering metric to use (e.g. 'si' for silhoute score or 'sf for score function).
        """
        scores = []
        for k in range(2, max_clusters + 1):
            # Cluster the data for each value of k
            score = silhouette_score(self.dataset, self.clusterings[k].labels_)
            scores.append(score)

        # Plot the scores vs. the number of clusters
        plt.plot(range(2, max_clusters + 1), scores, marker='o')
        plt.xlabel('Number of Clusters')
        plt.ylabel('Silhouette Score')
        plt.title('Silhouette Score vs. Number of Clusters')
        plt.show()

    if __name__ == "__main__":
        obj = KMeansClusterer()
        obj.main()