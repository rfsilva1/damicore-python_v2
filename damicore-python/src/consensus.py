import itertools as it

def get_partition_frequencies(clusterings):
    """
    Calculates the frequency of each partition across a set of clusterings.
    """
    partition_freqs = {}
    for clustering in clusterings:
        for partition in clustering.values():
            partition_freqs[partition] = partition_freqs.get(partition, 0) + 1
    return partition_freqs

def get_coclustering_frequencies(clusterings):
    """
    Calculates the frequency of each pair of items being in the same cluster.
    """
    if not clusterings:
        return {}, []

    items = sorted(clusterings[0].keys())
    coclustering_freqs = {}

    for i in range(len(items)):
        for j in range(i, len(items)):
            pair = (items[i], items[j])
            count = 0
            for clustering in clusterings:
                if clustering.get(pair[0]) == clustering.get(pair[1]):
                    count += 1
            coclustering_freqs[pair] = count / len(clusterings)

    return coclustering_freqs, items

def calculate_feature_importance(coclustering_frequencies, items):
    """
    Calculates the importance of each feature based on coclustering frequencies.
    """
    importance = {}
    for item in items:
        item_sum = 0
        for pair, freq in coclustering_frequencies.items():
            if item in pair:
                item_sum += (freq - 0.5)**2
        importance[item] = item_sum / len(items)
    return importance

def get_variable_pair_stability(coclustering_frequencies):
    """
    Calculates the stability of each pair of variables.
    """
    stability = {}
    for pair, freq in coclustering_frequencies.items():
        stability[pair] = 1 - 4 * (freq - 0.5)**2
    return stability
