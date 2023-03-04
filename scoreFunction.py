# Author: Tilo Reneau-Cardoso
# File: scoreFunction.py
# Description: The code was written for the Machine Learning 
# with Neural Signal course at Scripps College.

import numpy as np
import math

def d(x1,x2):
    # euclidean distance squared
    return np.dot(x1-x2,x1-x2)

def scoreFunction(X, kMeans,weight=1):
    """
    If I remember correctly sf score is a value between -1 and 1. Higher scores are better. 
    Score should be above 0; lower than 0 means your clustering agorithm is probably worse than random.
    If the scores are all 1 or the same value, try adjusting the weight variable; the equation contains the term
    
        e^e^(bcd - wcd)

    and bad things happen if the exponent gets too big so the weight value prevents that from happening:

        e^e^((bcd - wcd)/weight)

    See this paper for more info on sf score: https://link.springer.com/chapter/10.1007/978-3-540-73499-4_14
    
    Parameters
    ----------
    X : numpy.ndarray
        The data that was clustered.
    kMeans : sklearn.cluster.KMeans
        A KMeans object from the scikit-learn library that has already been fit to the data.
    weight : float, optional
        A weight to adjust the relative importance of bcd and wcd in the score. Default is 1.
    
    Returns
    -------
    float
        The clustering score.
    """
    k = kMeans.n_clusters
    #clusters = group_by_cluster(X, kMeans.labels_, k)
    labs =  kMeans.labels_
    centroids = kMeans.cluster_centers_
    
    z_tot = sum(X)/len(X)

    # computes between-cluster distance
    def bcd():
        bcd = 0
        for i in range(k):
            clust_i = X[labs == i]
            #clust_i = clusters[i]
            bcd += d(centroids[i],z_tot)*len(clust_i)
        return bcd/(len(X)*k)
    
    # computes within-cluster distacnce
    def wcd():
        wcd = 0
        for i in range(k):
            clust_i = X[labs == i]
            #clust_i = clusters[i]
            wcd += math.sqrt(sum([d(x, centroids[i]) for x in clust_i])/len(clust_i))
        return wcd/k

    bcd = bcd(); wcd = wcd();
    #return (wcd, bcd)
    #return (np.e**(np.e**(bcd-wcd)))   
    return 1 - 1/(np.e**(np.e**((bcd-wcd)/weight)  ))  