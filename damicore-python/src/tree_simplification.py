#!/usr/bin/python3

from tree import Node, Leaf, Edge
from math import log10, ceil
from random import Random

def num_digits(x):
  """Returns number of decimal digits in x.
  
  >>> num_digits(99)
  2
  >>> num_digits(100)
  2
  >>> num_digits(101)
  3
  """
  return int(ceil(log10(x)))

def artificial_ids(n):
  """Generates n artificial ids."""
  return ['_n{num:>0{max}}'.format(num=i, max=num_digits(n))
        for i in range(n)]

def matrix_argmin(m):
  """Returns indices of the minimum value in m."""
  indices = range(len(m))
  return min([(i,j) for i in indices for j in indices],
      key = lambda ij: m[ij[0]][ij[1]])

def calculate_q(m, sums):
  """Calculates matrix Q of the neighbor joining algorithm.
  
      The value Q_{ij} gives the decrease of total sum of edge lengths in the
  tree if nodes i and j are joined.
  """
  n = len(m)
  indices = range(n)
  q = [[0.0 for _ in indices] for _ in indices]

  for i, row in enumerate(m):
    for j, dij in enumerate(row):
      q[i][j] = (n - 2) * dij - sums[i] - sums[j]

  for i in indices:
    q[i][i] = float("inf")

  return q

def update_distance_matrix(m, sums, i, j):
  """Returns a new distance matrix with nodes i and j joined.

      The tuple (i,j) must be sorted. A new distance matrix is created with
  nodes i and j joined under a new node X. The node is placed at index i, and
  all its distances are updated.
  
  @return (new_m, di, dj) new distance matrix; distances i->X and j->X
  """
  n = len(m)
  dij, si, sj = m[i][j], sums[i], sums[j]

  di = (dij + (si - sj)/(n - 2))/2
  dj = (dij + (sj - si)/(n - 2))/2
  dk = [(m[i][k] + m[j][k] - dij)/2 for k in range(n)]

  new_m = [[dij for dij in row] for row in m]

  for k in range(n):
    new_m[i][k] = new_m[k][i] = dk[k]

  new_m.pop(j)
  for row in new_m:
    row.pop(j)

  return new_m, di, dj

def join_neighbors(tree, i, j, di, dj):
  r"""Returns a new tree with nodes i and j joined under a new node.

      [ (n_0)  ...  (n_i) ... (n_j)  ...  (n_N) ] --->

      [ (n_0)  ...     ()      ...  (n_{N-1}) ]
                   di /  \
                     /    \ dj
                   (n_i)   \
                         (n_j)
  """
  new_tree = [node for node in tree]
  new_tree[i] = Node(None,
      Edge(tree[i], di),
      Edge(tree[j], dj))
  new_tree.pop(j)
  return new_tree

def upgma(m, ids=None):
    """UPGMA algorithm."""
    n = len(m)
    if ids is None:
        ids = artificial_ids(n)

    # Turn m symmetric (and floating-point) if it's not already
    m = [
        [(m[i][j] + m[j][i]) / 2.0 for i in range(n)]
        for j in range(n)
    ]

    tree = [Leaf(id_) for id_ in ids]
    cluster_sizes = [1] * n

    curr_n = n
    while curr_n > 1:
        # Find closest clusters
        min_dist = float('inf')
        c1, c2 = -1, -1
        for i in range(curr_n):
            for j in range(i + 1, curr_n):
                if m[i][j] < min_dist:
                    min_dist = m[i][j]
                    c1, c2 = i, j

        # Merge clusters c1 and c2. New cluster at c1, c2 is removed.

        # Calculate new distances
        new_row = []
        for i in range(curr_n):
            if i != c1 and i != c2:
                dist = (cluster_sizes[c1] * m[c1][i] + cluster_sizes[c2] * m[c2][i]) / (cluster_sizes[c1] + cluster_sizes[c2])
                new_row.append(dist)

        # Update tree
        # The distance to the new node is half the distance between clusters
        dist = min_dist / 2.0
        if c1 > c2:
            c1, c2 = c2, c1 # ensure c1 < c2
        tree = join_neighbors(tree, c1, c2, dist, dist)

        # Update cluster sizes
        cluster_sizes[c1] += cluster_sizes[c2]
        cluster_sizes.pop(c2)

        # Update distance matrix
        # Rebuild row c1
        new_row_c1 = []
        new_row_idx = 0
        for i in range(curr_n):
            if i == c1:
                new_row_c1.append(0)
            elif i != c2:
                new_row_c1.append(new_row[new_row_idx])
                new_row_idx += 1

        m.pop(c2)
        for row in m:
            row.pop(c2)

        m[c1] = new_row_c1
        for i in range(len(m)):
            m[i][c1] = new_row_c1[i]

        curr_n -= 1

    return tree[0]

def neighbor_joining(m, ids=None):
  """Neighbor Joining algorithm.
  
      Given a distance matrix, the algorithm seeks a tree that approximates the
  measured distances by greedily choosing to join the pair of elements that
  minimize the total sum of edge lengths.
  """
  n = len(m)
  if ids is None:
    ids = artificial_ids(n)

  # Turn m symmetric (and floating-point) if it's not already
  m = [ 
      [(m[i][j] + m[j][i])/2.0 for i in range(n)]
      for j in range(n)]

  tree = [Leaf(id_) for id_ in ids]

  for _ in range(n, 2, -1):
    # Find closest neighbors
    s = list(map(sum, m))
    q = calculate_q(m, s)

    # Join neighbors and update distance matrix
    i, j = sorted(matrix_argmin(q))
    m, di, dj = update_distance_matrix(m, s, i, j)
    tree = join_neighbors(tree, i, j, di, dj)

  d = m[0][1]
  return join_neighbors(tree, 0, 1, d/2, d/2)[0]

def _random_joining(ids):
  """Generates a tree by repeatedly joining elements randomly."""
  r = Random()
  tree = [Leaf(id_) for id_ in ids]
  for _ in range(len(ids) - 1):
    i, j = sorted(r.sample(range(len(tree)), 2))
    tree = join_neighbors(tree, i, j, r.random(), r.random())

  return tree[0]

if __name__ == '__main__':
  from tree import test_tree
  expected_tree, m, ids = test_tree()
  tree = neighbor_joining(m, ids)

  print(tree, expected_tree)

  # Random test
  from tree import distance_matrix
  expected_tree = _random_joining(list(map(str, range(10))))
  m, ids = distance_matrix(expected_tree)
  tree = neighbor_joining(m, ids)
  print(tree, expected_tree)

  # Test for UPGMA
  print("\nTesting UPGMA...")
  m_upgma = [
      [0, 2, 4, 6],
      [2, 0, 4, 6],
      [4, 4, 0, 6],
      [6, 6, 6, 0]
  ]
  ids_upgma = ['A', 'B', 'C', 'D']
  tree_upgma = upgma(m_upgma, ids_upgma)
  print("UPGMA tree:", tree_upgma)
