#!/usr/bin/python3

import argparse
import os
import sys
import math
import ncd
import igraph
import tree_simplification as nj
from tree import newick_format, to_graph, relabel_leafs
from consensus import get_partition_frequencies, get_coclustering_frequencies, calculate_feature_importance, get_variable_pair_stability

def clustering(directory, compression_name='gzip', pairing_name='concat',
    is_parallel = True, tree_joining_algorithm='nj', verbose=1, **kwargs):
  if verbose > 0:
    sys.stderr.write('Performing NCD distance matrix calculation...\n')
  ncd_results = ncd.distance_matrix(directory, compression_name, pairing_name,
      is_parallel = is_parallel, verbose=verbose, **kwargs)

  if verbose > 0:
    sys.stderr.write('\nSimplifying graph...\n')
  m, ids = ncd.to_matrix(ncd_results)
  if tree_joining_algorithm == 'upgma':
      tree = nj.upgma(m, ids)
  else: # default to nj
      tree = nj.neighbor_joining(m, ids)

  if verbose > 0:
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

def generate_csv_report(data, filename):
    """Generates a consolidated CSV report from the analysis results."""
    with open(filename, 'w') as f:
        if 'fname_cluster' in data:
            f.write("Clustering Results\n")
            f.write("Filename,Cluster\n")
            for fname, cluster in data['fname_cluster'].items():
                f.write(f"{fname},{cluster}\n")
            f.write("\n")

        if 'feature_importance' in data:
            f.write("Feature Importance\n")
            f.write("Feature,Importance\n")
            for feature, importance in sorted(data['feature_importance'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{feature},{importance:.4f}\n")
            f.write("\n")

        if 'stability' in data:
            f.write("Variable Pair Stability\n")
            f.write("Pair,Frequency,Stability\n")
            f.write("Most Unstable Pairs\n")
            for pair, stab_score in data['stability']['unstable']:
                freq = data['coclustering_frequencies'][pair]
                f.write(f"{'-'.join(pair)},{freq:.4f},{1 - stab_score:.4f}\n")
            f.write("\n")
            f.write("Most Stable Pairs\n")
            for pair, stab_score in data['stability']['stable']:
                freq = data['coclustering_frequencies'][pair]
                f.write(f"{'-'.join(pair)},{freq:.4f},{1 - stab_score:.4f}\n")

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
  parser = argparse.ArgumentParser(add_help=False, parents=[ncd.cli_parser()])
  parser.add_argument('--ncd-output', help='File to output NCD result')
  parser.add_argument('--tree-output', help='File to output tree result')
  parser.add_argument('--graph-image', help='File to output graph image')
  parser.add_argument('--csv-report', help='File to output consolidated CSV report')
  parser.add_argument('-b', '--bootstrap', type=int, default=0,
      help='Number of bootstrap replicates for stability analysis')
  parser.add_argument('--feature-importance-output', help='File to output feature importance scores')
  parser.add_argument('--pair-stability-output', help='File to output variable pair stability scores')
  parser.add_argument('--layout', choices=['fr', 'cladogram'], default='fr',
      help='Graph layout algorithm (default: fr)')
  parser.add_argument('--tree-joining-algorithm', choices=['nj', 'upgma'], default='nj',
      help='Tree joining algorithm (default: nj)')
  a = parser.parse_args()

  verbose = 0 if a.no_verbose else a.verbose

  if not os.path.exists('tmp') or not os.path.isdir('tmp'):
    os.mkdir('tmp')
  if a.compressor == 'ppmd' and (
      not os.path.exists('ppmd_tmp') or not os.path.isdir('ppmd_tmp')):
    os.mkdir('ppmd_tmp')

  kwargs = {
      'pair_dir': 'tmp',
      'ppmd_tmp_dir': 'ppmd_tmp',
      'slowness': a.slowness,
      'model_order': a.model_order,
      'memory': a.memory,
      'block_size': a.block_size,
  }
  #
  ## end copied section ##

  report_data = {}
  if a.bootstrap > 0:
      import random
      import shutil
      from tree import relabel_leafs

      trees = []
      clusterings = []
      original_fnames = sorted(os.listdir(a.directory))
      original_fnames_paths = [os.path.join(os.path.abspath(a.directory), fname) for fname in original_fnames if os.path.isfile(os.path.join(a.directory, fname))]

      for i in range(a.bootstrap):
          if verbose > 0:
              sys.stderr.write('-- Bootstrap replicate {}/{} --\n'.format(i+1, a.bootstrap))

          bootstrap_dir = 'bootstrap_{}'.format(i)
          if os.path.exists(bootstrap_dir):
              shutil.rmtree(bootstrap_dir)
          os.mkdir(bootstrap_dir)

          bootstrapped_fnames_paths = random.choices(original_fnames_paths, k=len(original_fnames_paths))

          symlink_map = {}
          for j, fname_path in enumerate(bootstrapped_fnames_paths):
              symlink_name = 'file_{}'.format(j)
              os.symlink(fname_path, os.path.join(bootstrap_dir, symlink_name))
              symlink_map[symlink_name] = os.path.basename(fname_path)

          d = clustering(bootstrap_dir,
              compression_name = a.compressor, pairing_name = a.pairing,
              is_parallel = not a.serial, verbose=verbose, **kwargs)

          relabelled_tree = relabel_leafs(d['tree'], symlink_map)
          trees.append(relabelled_tree)

          relabelled_fname_cluster = {symlink_map[fname]: cluster for fname, cluster in d['fname_cluster'].items()}
          clusterings.append(relabelled_fname_cluster)

          shutil.rmtree(bootstrap_dir)

      coclustering_frequencies, items = get_coclustering_frequencies(clusterings)

      if verbose > 0:
          print("\n--- Analysis Report ---")

      # Feature importance
      importance = calculate_feature_importance(coclustering_frequencies, items)
      if verbose > 0:
          print("\nFeature Importance (higher is more important):")
          for item, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
              print("{}: {:.4f}".format(item, score))

      # Variable pair stability
      stability = get_variable_pair_stability(coclustering_frequencies)
      sorted_stability = sorted(stability.items(), key=lambda x: x[1])

      if verbose > 0:
          print("\nMost Unstable Pairs (frequency close to 0.5):")
          for pair, stab_score in sorted_stability[:5]:
              freq = coclustering_frequencies[pair]
              print("{}: frequency = {:.4f}, stability = {:.4f}".format(pair, freq, 1 - stab_score))

          print("\nMost Stable Pairs (frequency close to 0 or 1):")
          for pair, stab_score in sorted_stability[-5:]:
              freq = coclustering_frequencies[pair]
              print("{}: frequency = {:.4f}, stability = {:.4f}".format(pair, freq, 1 - stab_score))

      if a.feature_importance_output:
          with open(a.feature_importance_output, 'w') as f:
              f.write("feature,importance\n")
              for item, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                  f.write("{},{:.4f}\n".format(item, score))

      if a.pair_stability_output:
          with open(a.pair_stability_output, 'w') as f:
              f.write("pair,stability,frequency\n")
              for pair, stab_score in sorted_stability:
                  freq = coclustering_frequencies[pair]
                  f.write("{},{:.4f},{:.4f}\n".format('-'.join(pair), 1 - stab_score, freq))

      report_data['feature_importance'] = importance
      report_data['coclustering_frequencies'] = coclustering_frequencies
      report_data['stability'] = {
          'unstable': sorted_stability[:5],
          'stable': sorted_stability[-5:]
      }
  else:
      d = clustering(a.directory,
          compression_name = a.compressor, pairing_name = a.pairing,
          is_parallel = not a.serial, verbose=verbose, **kwargs)

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
        if a.layout == 'fr':
            seed_layout = g.layout('rt_circular', root=tree.content)
            layout = g.layout('fr', seed=seed_layout.coords,
                weights=calc_weights(g.es["length"]))
        else: # cladogram
            layout = g.layout_reingold_tilford(root=[g.vs.find(name=tree.content).index])
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
      report_data['fname_cluster'] = d['fname_cluster']

  if a.csv_report:
      generate_csv_report(report_data, a.csv_report)

