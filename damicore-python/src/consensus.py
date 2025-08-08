from collections import Counter
import tree

def get_partition_frequencies(trees):
    """
    Calculates the frequency of each partition in a list of trees.

    Args:
        trees: A list of tree objects.

    Returns:
        A Counter object mapping partitions to their frequencies.
    """
    all_partitions = []
    for t in trees:
        all_partitions.extend(list(tree.get_partitions(t)))

    return Counter(all_partitions)

def robinson_foulds_distance(tree1, tree2):
    """
    Calculates the Robinson-Foulds distance between two trees.
    """
    partitions1 = tree.get_partitions(tree1)
    partitions2 = tree.get_partitions(tree2)

    return len(partitions1.symmetric_difference(partitions2))

def get_coclustering_frequencies(clusterings):
    """
    Calculates the co-clustering frequency for each pair of items.
    """
    num_clusterings = len(clusterings)
    if not num_clusterings:
        return {}, []

    items = list(clusterings[0].keys())
    cocluster_counts = Counter()

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            item1 = items[i]
            item2 = items[j]

            count = 0
            for clustering in clusterings:
                if clustering.get(item1) == clustering.get(item2):
                    count += 1

            pair = tuple(sorted((item1, item2)))
            cocluster_counts[pair] = count

    cocluster_frequencies = {pair: count / num_clusterings for pair, count in cocluster_counts.items()}
    return cocluster_frequencies, items

def calculate_feature_importance(coclustering_frequencies, items):
    """Calculates feature importance from co-clustering frequencies."""
    importance = {item: 0.0 for item in items}
    num_items = len(items)
    if num_items <= 1:
        return importance

    for item1 in items:
        for item2 in items:
            if item1 != item2:
                pair = tuple(sorted((item1, item2)))
                importance[item1] += coclustering_frequencies.get(pair, 0.0)

    for item in items:
        importance[item] /= (num_items - 1)

    return importance

def get_variable_pair_stability(coclustering_frequencies):
    """
    Calculates the stability of variable pairs.
    Stability is defined as abs(frequency - 0.5), so it's low for frequencies close to 0.5.
    """
    stability = {}
    for pair, freq in coclustering_frequencies.items():
        stability[pair] = abs(freq - 0.5) * 2 # scale to [0,1]
    return stability
