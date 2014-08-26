import numpy as np
import os.path
import distances
from scipy.cluster.vq import vq, kmeans, whiten
from scipy.spatial.distance import euclidean, cosine
from scipy.stats import gaussian_kde
import preprocess
import PCA
from sklearn import mixture
import pickle

########################################################
# For the "main" section, see the bottom of this file. #
########################################################

distance_metric = 'euclidean' # alternatively 'cosine'
k_means_dist = euclidean # cosine

names = pickle.load(open('names.p', 'rb'))

def is_remix(s):
    return '.' in s

all_features = distances.features
release_indices = {}
for i in range(len(all_features)):
    release_indices[all_features[i][0]] = i

def split_to_originals_and_remixes(features):
    original_features = []
    remix_features = []
    for f in features:
        if is_remix(f[0]):
            remix_features.append(f)
        else:
            original_features.append(f)
    return original_features, remix_features


def ways():
    pass
    # Known bad / ineffective:
    k_means_set_on_union
    k_means_set
    gmm_set
    using_k_means
    using_gmm
    
    # Known mediocre:
    using_distance_to_original
    using_num_closer_than_original
    
    # Known good:
    using_half_k_means
    using_half_gmm
    using_whitened_distances # == whiten_and_call(using_distance_to_original)
    using_whitened_closer # == whiten_and_call(using_num_closer_than_original)
    
    pca_and_call
    
    ensemble_by_group


    # For strangeness ranking
    using_kde
    kde_on_all # Includes original mixes in the ranking


def run(iter=20):
    version = 1.2
    i = 0
    runs = []
    while i < iter:
        try:
            runs += [ensemble_all_together(version)]
            print "Iteration", i+1, "done."
        except:
            # Sometimes, k-means freaks out and throws an error
            i -= 1
        i += 1
    return average_methods_together(runs)

def ensemble_all_together(version=1.2):
    features = all_features
    #v 1.0:
    if version == 1.0:
        basic_functions = [ensemble_half_k_means, ensemble_half_gmm,
                           using_whitened_distances, using_whitened_closer]
    #v 1.1:
    elif version == 1.1:
        basic_functions = [ensemble_half_k_means, ensemble_half_gmm,
                           ensemble_distance_to_original, ensemble_num_closer,
                           using_kde]
    #v 1.2:
    else:
        basic_functions = [ensemble_half_k_means, ensemble_half_gmm,
                           ensemble_distance_to_original, ensemble_num_closer]
    basic_set = average_methods_together([fn(features) for fn in basic_functions])
    basic_pca_set = average_methods_together([ensemble_pca_on(features, fn) for fn in basic_functions])
    group_basic_set = average_methods_together([ensemble_by_group(fn) for fn in basic_functions])
    group_pca_set = average_methods_together([ensemble_by_group(ensemble_pca_on, fn) for fn in basic_functions])
    
    return average_methods_together([basic_set, basic_pca_set, group_basic_set, group_pca_set])

def ensemble_pca_on(features, fn, k=-1):
    pca_dimensions = [1, 2, 3, 5, 10]
    return average_methods_together([pca_and_call(features, fn, dim, k) for dim in pca_dimensions])

def ensemble_half_gmm(features):
    return average_methods_together([
        using_half_gmm_union(features, k=10),
        using_half_gmm_union(features, k=50),
        using_half_gmm_originals(features, k=10),
        using_half_gmm_originals(features, k=50)])

def ensemble_half_k_means(features):
    ks = [5, 10]
    return average_methods_together([using_half_k_means(features, k) for k in ks])

def ensemble_distance_to_original(features):
    return average_methods_together([using_distance_to_original(features), using_whitened_distances(features)])

def ensemble_num_closer(features):
    return average_methods_together([using_num_closer_than_original(features), using_whitened_closer(features)])

# Returns ranking of most novel to least novel
def using_distance_to_original(features=all_features):
    f_distances = distances.distances(features, distance_metric)
    remix_distances = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            # Original version.  Do nothing.
            continue
        original = str(int(float(release)))
        r_i = release_indices[release]
        o_i = release_indices[original]
        remix_distances += [(release, f_distances[r_i][o_i])]
    return sorted(remix_distances, key=lambda x: -1 * x[1])

# Returns ranking of most lovel to least novel
def using_num_closer_than_original(features=all_features):
    f_distances = distances.distances(features, distance_metric)
    num_nearer_neighbors = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            # Original version.  Do nothing. (Original has no base for comparison against.)
            continue
        original = str(int(float(release)))
        r_i = release_indices[release]
        o_i = release_indices[original]
        distance_to_original = f_distances[r_i][o_i]
        num_closer = 0
        for i in range(len(f_distances[r_i])):
            if i == r_i or is_remix(features[i][0]):
                continue
            if f_distances[r_i][i] < distance_to_original:
                num_closer += 1
        num_nearer_neighbors += [(release, num_closer)]
    return sorted(num_nearer_neighbors, key=lambda x: -1 * x[1])
    
# Returns set of novel remixes
def k_means_set_on_union(features=all_features, k=10):
    feature_matrix = np.zeros((len(features), len(features[0][1])))
    for i in range(len(features)):
        feature_matrix[i] = features[i][1]
    whitened = whiten(feature_matrix)
    means, distortion = kmeans(whitened, k, iter=20)
    
    feature_to_mean = {}
    for i in range(len(whitened)):
        feature = whitened[i]
        dists = np.zeros((k, 1))
        for j in range(k):
            dists[j] = k_means_dist(feature, means[j])
        feature_to_mean[features[i][0]] = np.argmin(dists)
    
    interesting = set()
    boring = set()
    for feature in features:
        release = feature[0]
        if int(float(release)) == float(release):
            # Original version.  Do nothing.
            continue
        original = str(int(float(release)))
        if feature_to_mean[release] != feature_to_mean[original]:
            interesting.add(release)
        else:
            boring.add(release)
    return interesting, boring

def k_means_set(features=all_features, k=10):
    feature_to_mean = get_feature_to_means(features, k)
    
    interesting = set()
    boring = set()
    for feature in features:
        release = feature[0]
        if not is_remix(release): #int(float(release)) == float(release):
            # Original version.  Do nothing.
            continue
        original = str(int(float(release)))
        if feature_to_mean[release] != feature_to_mean[original]:
            interesting.add(release)
        else:
            boring.add(release)
    return interesting, boring

def print_each_cluster(features=all_features, k=20):
    feature_to_mean = get_feature_to_means(features, k)
    mean_to_feature = {}
    for f in feature_to_mean:
        m = feature_to_mean[f]
        if m not in mean_to_feature:
            mean_to_feature[m] = set()
        mean_to_feature[m].add(f)
    i = 1
    for m in mean_to_feature:
        print "Cluster",i,":" 
        for f in mean_to_feature[m]:
            print name(f)
        print ""
        print ""
        i += 1

# Distance from remix's cluster's mean to original's
def using_k_means(features=all_features, k=10):
    feature_to_mean = get_feature_to_means(features, k)
    remix_distances = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        distance = k_means_dist(feature_to_mean[release], feature_to_mean[original])
        remix_distances += [(release, distance)]
    return sorted(remix_distances, key=lambda x: -1 * x[1])
   
# Distance from remix to original's cluster's mean     
def using_half_k_means(features=all_features, k=10):
    whitened_features = get_whitened_features(features)
    feature_to_mean = get_feature_to_means(features, k)
    remix_distances = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        try:
            distance = k_means_dist(whitened_features[release_indices[release]], feature_to_mean[original])
        except:
            print whitened_features[release_indices[release]]
            print feature_to_mean[original]
            raise
        remix_distances += [(release, distance)]
    return sorted(remix_distances, key=lambda x: -1 * x[1])

def pca_and_call(features=all_features, fn=using_distance_to_original, dim=2, k=-1):
    data = np.array([f[1] for f in features])
    # Note: this warps the variable data
    data_rescaled = PCA.PCA(data, dim)
    features = [(features[i][0], data_rescaled[i]) for i in range(len(features))]
    if k > 0:
        return fn(features, k)
    return fn(features)

def gmm_set_union(features=all_features, k=2):
    return gmm_set(features, k, True)

def gmm_set_originals(features=all_features, k=2):
    return gmm_set(features, k, False)

def gmm_set(features=all_features, k=2, union=False):
    originals, remixes = split_to_originals_and_remixes(features)
    if union:
        by_name, means = using_gmm_helper(features, features, k)
    else:
        by_name, means = using_gmm_helper(originals, features, k)
    interesting = set()
    boring = set()
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        if by_name[release] != by_name[original]:
            interesting.add(release)
        else:
            boring.add(release)
    return interesting, boring

def using_gmm_union(features=all_features, k=2):
    return using_gmm(features, k, True)

def using_gmm_originals(features=all_features, k=2):
    return using_gmm(features, k, False)

def using_gmm(features=all_features, k=2, union=False):
    originals, remixes = split_to_originals_and_remixes(features)
    if union:
        by_name, means = using_gmm_helper(features, features, k)
    else:
        by_name, means = using_gmm_helper(originals, features, k)
    remix_distances = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        distance = k_means_dist(means[by_name[release]], means[by_name[original]])
        remix_distances += [(release, distance)]
    return sorted(remix_distances, key=lambda x: -1 * x[1])

def using_half_gmm_union(features=all_features, k=2):
    return using_half_gmm(features, k, True)

def using_half_gmm_originals(features=all_features, k=2):
    return using_half_gmm(features, k, False)

def using_half_gmm(features=all_features, k=2, union=False):
    originals, remixes = split_to_originals_and_remixes(features)
    if union:
        by_name, means = using_gmm_helper(features, features, k)
    else:
        by_name, means = using_gmm_helper(originals, features, k)
    remix_distances = []
    for feature in features:
        release = feature[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        distance = k_means_dist(feature[1], means[by_name[original]])
        remix_distances += [(release, distance)]
    return sorted(remix_distances, key=lambda x: -1 * x[1])

# Evaluate_at should be a superset of features.  features is either only originals or all.  evaluate at is all.
def using_gmm_helper(features, evaluate_at, k):
    to_fit = np.array([f[1] for f in features])
    to_evaluate = np.array([f[1] for f in evaluate_at])
    
    g = mixture.GMM(n_components=k)
    g.fit(to_fit)
    predictions = g.predict(to_evaluate)
    by_name = {}
    for i in range(len(evaluate_at)):
        by_name[evaluate_at[i][0]] = predictions[i]
    return by_name, g.means_

def using_kde(features=all_features):
    return filter(lambda x: is_remix(x[0]), using_kde_helper(features, features))

# Ratio of commonness of remix to original
# If remix had density of 0.5 and original had 1, ratio is 0.5; lower = stranger remix
def kde_ratio_to_original(features=all_features):
    kde_values = using_kde_helper(features, features)
    dict_form = {}
    for pair in kde_values:
        dict_form[pair[0]] = pair[1]
    ratios = []
    for pair in kde_values:
        release = pair[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        ratios += [(release, dict_form[release] / dict_form[original])]
    return sorted(ratios, key=lambda x: x[1])

# Lower ranking number = more strange. so if return negative, release was stranger than original
# Larger = less strange
def kde_ranking_difference_to_original(features=all_features):
    kde_values = using_kde_helper(features, features)
    ranknums = enumerate_ranking_from_list(kde_values)
    ratios = []
    for pair in kde_values:
        release = pair[0]
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        ratios += [(release, ranknums[release] - ranknums[original])]
    return sorted(ratios, key=lambda x: x[1])

def kde_on_all(features=all_features):
    return using_kde_helper(features, features)

# This has nans everywhere, so is unusable in practice.
# Maybe this implementation of KDE is not meant to be used on non-input points?
#def using_original_kde(features=all_features):
#    originals, remixes = split_to_originals_and_remixes(features)
#    return using_kde_helper(originals, remixes)


# Less dense = more novel
def using_kde_helper(features, evaluate_at):
    feature_matrix = np.array([f[1] for f in features]).T
    to_evaluate = np.array([f[1] for f in evaluate_at]).T
    kde = gaussian_kde(feature_matrix)
    evaluated = kde(to_evaluate)
    by_name = []
    for i in range(len(evaluate_at)):
        by_name += [(evaluate_at[i][0], evaluated[i])]
    return sorted(by_name, key=lambda x: x[1])
    

# No extra args because we don't need to use this with functions that
# ask for k -- they already whiten their features.
def whiten_and_call(features=all_features, fn=using_distance_to_original):
    return fn(get_whitened_features_with_releases(features))

def get_whitened_features_with_releases(features):
    whitened_vectors = get_whitened_features(features)
    whitened_features = features[:]
    for i in range(len(whitened_features)):
        whitened_features[i] = (whitened_features[i][0], whitened_vectors[i])
    return whitened_features

def using_whitened_distances(features=all_features):
    return whiten_and_call(features, using_distance_to_original)

def using_whitened_closer(features=all_features):
    return whiten_and_call(features, using_num_closer_than_original)

def get_feature_to_means(features, k):
    original_features, remix_features = split_to_originals_and_remixes(features)
    whitened_originals = get_whitened_features(original_features)
    whitened_remixes = get_whitened_features(remix_features)
    
    means, distortion = kmeans(whitened_originals, k, iter=20)
    
    feature_to_mean = {}
    add_feature_to_mean_mapping(feature_to_mean, whitened_originals, original_features, k, means)
    add_feature_to_mean_mapping(feature_to_mean, whitened_remixes, remix_features, k, means)
    
    return feature_to_mean

def get_whitened_features(f):
    matrix_form = np.zeros((len(f), len(f[0][1])))
    for i in range(len(f)):
        matrix_form[i] = f[i][1]
    whitened = whiten(matrix_form)
    return whitened

def add_feature_to_mean_mapping(dest, whitened_features, features, k, means):
    for i in range(len(whitened_features)):
        feature = whitened_features[i]
        dists = np.zeros((k, 1))
        for j in range(k):
            dists[j] = k_means_dist(feature, means[j])
        dest[features[i][0]] = means[np.argmin(dists)]

def ensemble_by_group(fn, *args):
    r_features = reprocess(preprocess.rhythm, all_features[:])
    p_features = reprocess(preprocess.pitch, all_features[:])
    m_features = reprocess(preprocess.mfccs, all_features[:])
    
    r_list = fn(r_features, *args)
    p_list = fn(p_features, *args)
    m_list = fn(m_features, *args)
    
    return average_methods_together([r_list, p_list, m_list])

def enumerate_ranking_from_list(l):
    rankings = {}
    for i in range(len(l)):
        rankings[l[i][0]] = i
    return rankings

def enumerate_norm_ranking_from_list(l):
    rankings = {}
    for i in range(len(l)):
        rankings[l[i][0]] = i * 100.0 / (len(l) - 1)
    return rankings

def average_methods_together(lists):
    rankings = []
    for l in lists:
        rankings += [enumerate_ranking_from_list(l)]
    overall_rankings = {}
    for release in rankings[0].keys():
        overall_rankings[release] = np.sum([r[release] for r in rankings])
    to_return = overall_rankings.keys()
    to_return = [(x, []) for x in to_return]
    return sorted(to_return, key=lambda x: overall_rankings[x[0]])

def reprocess(fn, features):
    for i in range(len(features)):
        features[i] = (features[i][0], fn(features[i][1]))
    return features

def name(release):
    return names[release]

def top_20(fn):
    if type(fn) == type([]):
        ranking = fn
    else:
        ranking = fn()
    for i in range(20):
        print name(ranking[i][0])

def bottom_20(fn):
    if type(fn) == type([]):
        ranking = fn
    else:
        ranking = fn()
    to_print = ranking[len(ranking) - 20:]
    for t in to_print:
        print name(t[0])

def all_rankings(fn):
    if type(fn) == type([]):
        ranking = fn
    else:
        ranking = fn()
    for i in range(len(ranking)):
        print i, name(ranking[i][0])

def all_rankings_norm(fn):
    if type(fn) == type([]):
        ranking = fn
    else:
        ranking = fn()
    for i in range(len(ranking)):
        print '%.2f' % (i * 100.0 / (len(ranking) - 1)), '\t', name(ranking[i][0])

def non_above_beyond_rankings(fn):
    if type(fn) == type([]):
        ranking = fn
    else:
        ranking = fn()
    ranking = filter(lambda x: "beyond -" not in name(x[0])[0].lower(), ranking)
    ranking = filter(lambda x: "beyond-" not in name(x[0])[0].lower(), ranking)
    ranking = filter(lambda x: "oceanlab" not in name(x[0])[0].lower(), ranking)
    for i in range(len(ranking)):
        print i, name(ranking[i][0])

def average_above_beyond_ranking(ranking):
    rdict = enumerate_norm_ranking_from_list(ranking)
    releases = rdict.keys()
    r1 = filter(lambda x: "beyond -" in name(x)[0].lower(), releases)
    r2 = filter(lambda x: "beyond-" in name(x)[0].lower(), releases)
    r3 = filter(lambda x: "oceanlab" in name(x)[0].lower(), releases)
    r4 = filter(lambda x: "tranquility" in name(x)[0].lower(), releases)
    releases = r1
    releases.extend(r2)
    releases.extend(r3)
    releases.extend(r4)
    return np.mean([rdict[r] for r in releases])

def print_novelty_and_strangeness(novelty, strangeness, by_novelty=True, threshold=209):
    n_dict = enumerate_ranking_from_list(novelty)
    s_dict = enumerate_ranking_from_list(strangeness)
    both = {}
    for k1 in n_dict:
        for k2 in s_dict:
            if k1 == k2:
                both[k1] = {'novelty':n_dict[k1], 'strangeness':s_dict[k2]}
    if by_novelty:
        keys = [r[0] for r in novelty if r[0] in both.keys()]
    else:
        keys = [r[0] for r in strangeness if r[0] in both.keys()]
    for k in keys:
        if (both[k]['novelty'] <= threshold and both[k]['strangeness'] >= 209 - threshold) or (both[k]['novelty'] >= 209 - threshold and both[k]['strangeness'] <= threshold):
            print both[k], '\t', name(k)

def print_normalized_strangeness_difference(ranking):
    kde_all = enumerate_ranking_from_list(ranking)
    n = float(len(kde_all.keys()) - 1)
    differences = {}
    for release in kde_all:
        if not is_remix(release):
            continue
        original = str(int(float(release)))
        differences[release] = (kde_all[release] - kde_all[original]) * 100.0 / n
    releases = sorted(differences.keys(), key=lambda x: differences[x])
    for r in releases:
        print '%.2f' % (differences[r]), '\t', name(r)
    print 'Average Remix KDE Value [0, 100]:', np.mean([kde_all[k] for k in kde_all.keys() if is_remix(k)]) / 3.18

novelty_ranking = pickle.load(open('20_runs_averaged_v1.2_euclidean.p', 'rb'))
strangeness_ranking = kde_on_all()

if __name__ == '__main__':
    # Interesting calls using the two main rankings used in the writeup
    print_novelty_and_strangeness(novelty_ranking, strangeness_ranking, by_novelty=True)
    #top_20(novelty_ranking)
    #top_20(strangeness_ranking)
    #bottom_20(novelty_ranking)
    #bottom_20(strangeness_ranking)
    #non_above_beyond_rankings(novelty_ranking)
    #non_above_beyond_rankings(strangeness_ranking)
    #print average_above_beyond_ranking(novelty_ranking)
    #print average_above_beyond_ranking(strangeness_ranking)
    #all_rankings(novelty_ranking)
    #all_rankings(strangeness_ranking)
    #all_rankings_norm(novelty_ranking)
    #all_rankings_norm(strangeness_ranking)
    #print_normalized_strangeness_difference(strangeness_ranking)
    
    # Examples of calls you can do yourself
    #top_20(using_distance_to_original)
    #bottom_20(using_num_closer_than_original)
    #all_rankings_norm(using_half_k_means)
    #top_20(pca_and_call(fn=using_half_gmm_union, dim=5, k=20))
    #top_20(whiten_and_call(fn=using_distance_to_original))
    #top_20(ensemble_by_group(using_half_gmm, 5))
    #top_20(ensemble_by_group(pca_and_call, using_num_closer_than_original, 8))
    #top_20(ensemble_by_group(pca_and_call, using_half_gmm_originals, 3, 10))
    
