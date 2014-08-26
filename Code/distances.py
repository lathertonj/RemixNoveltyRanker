from scipy.spatial import distance
import numpy as np
from preprocess import preprocess
import featurize

def features():
    f = open(featurize.file)
    first_line = f.readline()
    feature = f.readline()
    features = [] # Don't use dict, we want to preserve an order
    while feature != "" and feature != '\n':
        #stuff
        feature = feature.strip().split(',')
        release = feature[0]
        vector = [float(x) for x in feature[1:]]
        features += [(release, preprocess(vector))]
        feature = f.readline()
    f.close()
    return features

features = features()

def distances(features, method='euclidean'):
    n = len(features)
    d = len(features[0][1])
    np_features = np.zeros((n, d))
    for i in range(n):
        np_features[i] = features[i][1] # features[i] is (release, vector)
    d = distance.pdist(np_features, method)
    return distance.squareform(d, 'tomatrix')


def find_most_distant_release(r, d_mat = distances(features)):
    r_index = -1
    r = str(r)
    for i in range(len(features)):
        if features[i][0] == r:
            r_index = i
    if r_index == -1:
        return "release %s not found" % r
    return features[np.argmax(d_mat[r_index])][0]
    
def find_closest_release(r, d_mat = distances(features)):
    r_index = -1
    r = str(r)
    for i in range(len(features)):
        if features[i][0] == r:
            r_index = i
    if r_index == -1:
        return "release %s not found" % r
    # d_mat[r_index][r_index] == 0 so let's make it something larger.
    to_look_through = np.array(d_mat[r_index])
    to_look_through[r_index] = np.inf
    return features[np.argmin(to_look_through)][0]
    