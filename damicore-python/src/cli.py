import argparse
import os
import sys

def get_base_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('directory',
        help='Directory containing files to compare')

    parser.add_argument('-c', '--compressor', choices=['gzip', 'bzip2', 'ppmd'],
        default='gzip', help='Compressor to use (default: gzip)')
    parser.add_argument('-P', '--pairing', choices=['concat', 'interleave'],
        default='concat', help='Pairing method to use (default: concat)')

    compressor_group = parser.add_argument_group('Compressor options',
        'Options to control compressor behavior')
    compressor_group.add_argument('--slowness', '--gzip-slowness',
        '--bzip2-slowness', default=6, type=int,
        help='(gzip, bzip2) slowness of compression (1-9): ' +
        '1 is faster, 9 is best compression')
    compressor_group.add_argument('--model-order', '--ppmd-model-order',
        default=6, type=int,
        help='(ppmd) model order (2-16): 2 is faster, 16 is best')
    compressor_group.add_argument('--memory', '--ppmd-memory',
        default=10, type=int, help='(ppmd) maximum memory, in MiB (1-256)')
    compressor_group.add_argument('--block-size', '--interleave-block-size',
        default=1024, type=int,
        help='(interleave) block size for interleaving, in bytes')

    misc_group = parser.add_argument_group('General options')

    is_serial = misc_group.add_mutually_exclusive_group()
    is_serial.add_argument('--serial', action='store_true',
        help='Compute compressions serially')
    is_serial.add_argument('--parallel', action='store_true',
        help='Compute compressions in parallel (default)')

    misc_group.add_argument('-v', '--verbose', action='count',
        help='Verbose output. Repeat to increase verbosity level (default: 1)',
        default = 1)
    misc_group.add_argument('--no-verbose', action='store_true',
        help='Turn verbosity off')
    misc_group.add_argument('-V', '--version', action='version', version='0.0.1')
    misc_group.add_argument('--tree-joining-algorithm', choices=['nj', 'upgma'], default='nj',
                        help='Tree joining algorithm to use (default: nj)')
    return parser

def prepare_environment(args):
    """Prepares environment for execution, creating directories."""
    verbose = 0 if args.no_verbose else args.verbose
    if verbose != 1:
        sys.stderr.write('Note: verbosity level not implemented yet\n')

    if not os.path.exists('tmp') or not os.path.isdir('tmp'):
        os.mkdir('tmp')
    if args.compressor == 'ppmd' and (
        not os.path.exists('ppmd_tmp') or not os.path.isdir('ppmd_tmp')):
        os.mkdir('ppmd_tmp')

    kwargs = {
        'pair_dir': 'tmp',
        'ppmd_tmp_dir': 'ppmd_tmp',
        'slowness': args.slowness,
        'model_order': args.model_order,
        'memory': args.memory,
        'block_size': args.block_size,
    }
    return kwargs
