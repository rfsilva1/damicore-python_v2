#!/usr/bin/python3

import argparse
import os
import sys
import math
import ncd
import igraph
import tree_simplification as nj
from tree import newick_format, to_graph
from cli import get_base_parser, prepare_environment

def clustering(directory, compression_name='gzip', pairing_name='concat',
    is_parallel = True, tree_joining_algorithm='nj', **kwargs):
  sys.stderr.write('Performing NCD distance matrix calculation...\n')
  ncd_results = ncd.distance_matrix(directory, compression_name, pairing_name,
      is_parallel = is_parallel, **kwargs)

  sys.stderr.write('\nSimplifying graph...\n')
  m, ids = ncd.to_matrix(ncd_results)
  if tree_joining_algorithm == 'upgma':
      tree = nj.upgma(m, ids)
  else: # default to nj
      tree = nj.neighbor_joining(m, ids)

  sys.stderr.write('\nClustering elements...\n')
  g = to_graph(tree)
  fast_newman = g.community_fastgreedy(weights="length").as_clustering()

  # Maps leaf ID to cluster number
  vertex_names = [v["name"] for v in g.vs]
  membership = {}
  for id_ in ids:
    membership[id_] = fast_newman.membership[ vertex_names.index(id_) ]

  return {
      'ncd': ncd_results,
      'tree': tree,
      'fnames': ids,
      'graph': g,
      'node_clustering': fast_newman,
      'fname_cluster': membership,
  }

def calc_weights(lengths, min_length=1):
  n = len(lengths)
  mean = float(sum(lengths)) / n
  var = sum((l - mean)**2 for l in lengths) / n
  stddev = math.sqrt(var)
  scores = [(l - mean)/stddev for l in lengths]
  min_score = min(scores)
  norm_length = [min_length + (score - min_score) for score in scores]
  return norm_length

if __name__ == '__main__':
  base_parser = get_base_parser()
  parser = argparse.ArgumentParser(
      description='DAMICORE is an easy-to-use clustering and classification tool.',
      parents=[base_parser])
  parser.add_argument('-o', '--output', help='output file (default: stdout)')
  parser.add_argument('--ncd-output', help='File to output NCD result')
  parser.add_argument('--tree-output', help='File to output tree result')
  parser.add_argument('--graph-image', help='File to output graph image')
  parser.add_argument('--format', choices=['csv', 'phylip'],
      help='Choose matrix format (default: csv) for the NCD output file')
  a = parser.parse_args()

  kwargs = prepare_environment(a)

  d = clustering(a.directory,
      compression_name = a.compressor, pairing_name = a.pairing,
      is_parallel = not a.serial, tree_joining_algorithm = a.tree_joining_algorithm, **kwargs)

  # Outputs NCD step
  if a.ncd_output is not None:
    ncd_results = d['ncd']
    if a.format == 'phylip':
      ncd_out = ncd.phylip_format(ncd_results)
    else:
      ncd_out = ncd.csv_format(ncd_results)
    with open(a.ncd_output, 'wt') as f:
      f.write(ncd_out)

  # Outputs tree in Newick format
  if a.tree_output is not None:
    tree = d['tree']
    with open(a.tree_output, 'wt') as f:
      f.write(newick_format(tree))

  # Outputs graph image
  # TODO(brunokim): use a dendogram layout, which igraph seems to be lacking
  if a.graph_image is not None:
    g = d['graph']
    node_clustering = d['node_clustering']
    fnames = d['fnames']
    tree = d['tree']

    style = {}
    seed_layout = g.layout('rt_circular', root=tree.content)

    layout = g.layout('fr', seed=seed_layout.coords,
        weights=calc_weights(g.es["length"]))
    style['layout'] = layout
    style['vertex_size'] = [
        3 if v['name'] not in fnames else 10
        for v in g.vs]
    style['vertex_label'] = [
        '' if v['name'] not in fnames else v['name']
        for v in g.vs]
    igraph.plot(node_clustering, target=a.graph_image, **style)

  # Output cluster membership
  out = 'filename,cluster\n'
  for fname, cluster in d['fname_cluster'].items():
    out += '%s,%d\n' % (fname, cluster)

  if a.output is None:
    print(out)
  else:
    with open(a.output, 'wt') as f:
      f.write(out)

