#!/usr/bin/env python

"""High-level wrapper for intphys data generation

This programm wraps the intphys binary (as packaged by Unreal Engine)
into a simple to use command-line interface. It defines few
environment variables (namely input JSon scenes file, output
directory and random seed), launch the binary and filter its log
messages at runtime, keeping only relevant messages.

The INTPHYS_BINARY variable must be defined in your environment
(this is done for you by the activate-intphys script).

To see command-line arguments, have a::

    ./intphys.py --help

"""

import argparse
import atexit
import copy
import json
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading


# absolute path to the directory containing this script
INTPHYS_ROOT = os.path.dirname(os.path.abspath(__file__))

# path to the UnrealEngine directory
UE_ROOT = os.path.join(INTPHYS_ROOT, 'UnrealEngine')

# the default screen resolution (in pixels)
DEFAULT_RESOLUTION = '288x288'


def intphys_binaries():
    """Returns the list of packaged intphys programs as absolute paths"""
    path = os.path.join(
        INTPHYS_ROOT, 'Package/LinuxNoEditor/intphys/Binaries/Linux')

    if os.path.isdir(path):
        return [os.path.join(path, bin) for bin in os.listdir(path)]
    else:
        print('WARNING: intphys package not found')
        return []


class LogStripFormatter(logging.Formatter):
    """Strips trailing \n in log messages"""
    def format(self, record):
        record.msg = record.msg.strip()
        return super(LogStripFormatter, self).format(record)


class LogUnrealFormatter(LogStripFormatter):
    """Removes begining date, module name and trailing '\n'"""
    def format(self, record):
        # remove all content before and including the second ':' (this
        # strip off the date and id from Unreal log messages)
        try:
            record.msg = record.msg[
                [m.start() for m in re.finditer(':', record.msg)][1]+1:]
        except IndexError:
            pass

        return super(LogUnrealFormatter, self).format(record)


class LogNoEmptyMessageFilter(logging.Filter):
    """Inhibits empty log messages (spaces only or \n)"""
    def filter(self, record):
        return len(record.getMessage().strip())


class LogNoStartupMessagesFilter(logging.Filter):
    """Removes luatorch import messages and unreal startup messages"""
    def filter(self, record):
        msg = record.getMessage()
        return not (
            'Using binned.' in msg or
            'per-process limit of core file size to infinity.' in msg or
            'depot+UE4-Releases' in msg)


class LogInhibitUnrealFilter(logging.Filter):
    """Inhibits some unrelevant Unreal log messages

    Messages containing 'Error:' or 'LogScriptPlugin' are kept, other
    are removed from the Unreal Engine log (messages like
    "[data][id]message")

    """
    def filter(self, record):
        msg = record.getMessage()
        return (not re.search('\[.*\]\[.*\]', msg) or
                'Error:' in msg or
                'LogScriptPlugin' in msg)


def GetLogger(verbose=False, name=None):
    """Returns a logger configured to filter Unreal log messages

    If `verbose` is True, do not filter any message, if `verbose` is
    False (default), keep only relevant messages).

    If `name` is not None, prefix all messages with it.

    """
    msg = '{}%(message)s'.format('{}: '.format(name) if name else '')

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addFilter(LogNoEmptyMessageFilter())

    if not verbose:
        log.addFilter(LogInhibitUnrealFilter())
        log.addFilter(LogNoStartupMessagesFilter())
        formatter = LogUnrealFormatter(msg)
    else:
        formatter = LogStripFormatter(msg)

    # log to standard output
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    std_handler.setLevel(logging.DEBUG)
    log.addHandler(std_handler)

    return log


def ParseArgs():
    """Defines a commndline argument parser and returns the parsed arguments"""

    parser = argparse.ArgumentParser(
        description='Data generator for the intphys project')

    parser.add_argument(
        'scenes_file', metavar='<json-file>', help='''
        json configuration file defining the scenes to be rendered,
        for an exemple configuration file see {}'''
        .format(os.path.join(INTPHYS_ROOT, 'Exemples', 'exemple.json')))

    parser.add_argument(
        '-o', '--output-dir', metavar='<output-dir>', default=None, help='''
        directory where to write generated data, must be non-existing
        or used along with the --force option. If <output-dir> is not
        specified, the program run in "dry mode" and do not save any data.''')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='display all the UnrealEngine log messages')

    parser.add_argument(
        '-r', '--resolution', default=DEFAULT_RESOLUTION,
        metavar='<width>x<height>',
        help='resolution of the rendered images (in pixels)')

    parser.add_argument(
        '-s', '--seed', default=None, metavar='<int>', type=int,
        help='optional random seed for data generator, '
        'by default use the current system time')

    parser.add_argument(
        '-f', '--force', action='store_true',
        help='overwrite <output-dir>, any existing content is erased')

    # parser.add_argument(
    #     '-j', '--njobs', type=int, default=1, metavar='<int>',
    #     help='''number of data generation to run in parallel,
    #     this option is ignored if --editor is specified''')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-e', '--editor', action='store_true',
        help='launch the intphys project in the UnrealEngine editor')

    group.add_argument(
        '-g', '--standalone-game', action='store_true',
        help='launch the project as a standalone game (relies on UE4Editor)')

    args = parser.parse_args()
    if not re.match('[0-9]+x[0-9]+', args.resolution):
        raise IOError('resolution is not in <width>x<height> format'
                      '(e.g. "800x600"): {}'.format(args.resolution))

    return args


def _BalanceList(l, n):
    """Balance the elements of a list of integers into `n` sublists

    This is used for subjobs configuration generation. Sublists with
    only zeros are removed.

    >>> balance_list([5, 1, 2], 2) == [[3, 0, 1], [2, 1, 1]]
    >>> balance_list([1, 0], 2) == [[1, 0]]

    """
    balanced = [[(v / n if v >= n else 0) for v in l] for _ in range(n)]

    idx = 0
    for i, v in enumerate(l):
        if v < n:
            for j in range(v):
                balanced[(j + idx) % n][i] = 1
            idx += v

    idx = 0
    for i, v in enumerate(l):
        diff = v - sum(s[i] for s in balanced)
        if diff:
            balanced[idx][i] += diff
            idx = (idx + 1) % n

    balanced = [s for s in balanced if sum(s)]

    for i in range(len(l)):
        assert sum(b[i] for b in balanced) == l[i]

    return balanced


# def _BalanceConfig(config, njobs):
#     """Split the `config` into `n` parts returned as list of dicts

#     Return a tuple (subconfigs, nruns, njobs) where subconfigs is a
#     list of JSON dicts, each one being the configuration of a
#     subjob. `nruns` is a list of the total number of runs in each
#     subjob. `njobs` can be modified and is returned as the third
#     element in the pair.

#     """
#     # compute the list of balanced subjobs (from nested nested dict to
#     # list of dicts or ints)
#     values = [v for vv in config.itervalues() for v in vv.itervalues()]
#     # from list of dicts or ints to nested list
#     values = [v.values() if isinstance(v, dict) else [v] for v in values]
#     # from nested list to list
#     values = sum(values, [])

#     balanced = _BalanceList(values, njobs)
#     nruns = [sum(l) for l in balanced]

#     if njobs > len(balanced):
#         njobs = len(balanced)
#         print('reducing the number of jobs to {}'.format(njobs))

#     # create subconfigs for each subjob (from list to nested nested dict)
#     subconfigs = [copy.deepcopy(config) for _ in range(njobs)]
#     for i in range(njobs):
#         for block_name, block_value in config.iteritems():
#             j = 0
#             for set_name, set_value in block_value.iteritems():
#                 if isinstance(set_value, dict):  # test iteration
#                     for subset_name in set_value.iterkeys():
#                         subconfigs[i][block_name][set_name][subset_name] = (
#                             balanced[i][j])
#                         j += 1
#                 else:  # train iteration
#                     subconfigs[i][block_name][set_name] = balanced[i][j]
#                     j += 1

#     return subconfigs, nruns, njobs


def _Run(command, log, scenes_file, output_dir, cwd=None,
         seed=None, dry=False, resolution=DEFAULT_RESOLUTION):
    """Run `command` as a subprocess

    The `command` stdout and stderr are forwarded to `log`. The
    `command` runs with the following environment variables, in top of
    the current environment:

    INTPHYS_SCENES is the absolute path to `SCENES_file`.

    INTPHYS_DATA is the absolute path to `output_dir` with a
       trailing slash added.

    INTPHYS_SEED is `seed`

    INTPHYS_DRY is `dry`

    INTPHYS_RESOLUTION is `resolution`

    """
    # get the output directory as absolute path
    output_dir = os.path.abspath(output_dir)

    # setup the environment variables used in python scripts
    environ = copy.deepcopy(os.environ)
    environ['INTPHYS_ROOT'] = INTPHYS_ROOT
    environ['INTPHYS_DATADIR'] = output_dir
    environ['INTPHYS_SCENES'] = os.path.abspath(scenes_file)
    environ['INTPHYS_RESOLUTION'] = resolution

    if dry:
        environ['INTPHYS_DRY'] = 'true'
        log.info('running in dry mode, dont save anything')
    else:
        log.info('write data to ' + output_dir)

    if seed is not None:
        environ['INTPHYS_SEED'] = str(seed)

    # run the command as a subprocess
    job = subprocess.Popen(
        shlex.split(command),
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=environ)

    # join the command output to log (from
    # https://stackoverflow.com/questions/35488927)
    def ConsumeLines(pipe, consume):
        with pipe:
            # NOTE: workaround read-ahead bug
            for line in iter(pipe.readline, b''):
                consume(line.decode('utf8'))
            consume('\n')

    threading.Thread(
        target=ConsumeLines,
        args=[job.stdout, lambda line: log.info(line)]).start()

    # wait the job is finished, forwarding any error
    job.wait()
    if job.returncode:
        log.error('command "%s" returned with %s', command, job.returncode)
        sys.exit(job.returncode)


def RunBinary(output_dir, scenes_file, njobs=1, seed=None,
              dry=False, resolution=DEFAULT_RESOLUTION, verbose=False):
    """Run the intphys packaged binary as a subprocess

    If `njobs` is greater than 1, split the json configuration file
    into subparts of equivalent workload and run several jobs in
    parallel

    """
    if type(njobs) is not int or njobs < 1:
        raise IOError('njobs argument must be a strictly positive integer')

    # overload binary if defined in the environment
    if 'INTPHYS_BINARY' in os.environ:
        intphys_binary = os.environ['INTPHYS_BINARY']
    else:
        intphys_binary = intphys_binaries()[0]

    if not os.path.isfile(intphys_binary):
        raise IOError('No such file: {}'.format(intphys_binary))

    if not os.path.isfile(scenes_file):
        raise IOError('Json file not found: {}'.format(scenes_file))

    print('running {}{}'.format(
        intphys_binary,
        '' if njobs == 1 else ' in {} jobs'.format(njobs)))

    if njobs == 1:
        _Run(intphys_binary,
             GetLogger(verbose=verbose),
             scenes_file, output_dir, seed=seed, dry=dry,
             resolution=resolution)
    else:
        raise NotImplementedError('njobs option not yet implemented')
        # # split the json configuration file into balanced subparts
        # subconfigs, nruns, njobs = _BalanceConfig(
        #     json.load(open(config_file, 'r')), njobs)

        # # increase artificially the nruns to have margin for retries
        # # (this can occur for test runs)
        # nruns = [10 * r for r in nruns]

        # # write them in subdirectories
        # for i, config in enumerate(subconfigs, 1):
        #     path = os.path.join(output_dir, str(i))
        #     os.makedirs(path)
        #     open(os.path.join(path, 'config.json'), 'w').write(
        #         json.dumps(config, indent=4))

        # # parallel must defines a different seed for each job
        # seed = int(round(time.time() * 1000)) if seed is None else seed

        # # define arguments list for each jobs
        # _out = [os.path.join(output_dir, str(i)) for i in range(1, njobs+1)]
        # _conf = [os.path.join(output_dir, str(i), 'config.json')
        #          for i in range(1, njobs+1)]
        # _seed = [str(seed + sum(nruns[:i])) for i in range(njobs)]
        # _log = [GetLogger(name='job {}'.format(i))
        #         for i in range(1, njobs+1)]

        # # run the subprocesses
        # joblib.Parallel(n_jobs=njobs, backend='threading')(
        #     joblib.delayed(_Run)(
        #         INTPHYS_BINARY, _log[i], _conf[i], _out[i],
        #         seed=_seed[i], dry=dry, resolution=resolution)
        #     for i in range(njobs))


def RunEditor(output_dir, scenes_file, seed=None, dry=False,
              resolution=DEFAULT_RESOLUTION, verbose=False,
              standalone_game=False):
    """Run the intphys project within the UnrealEngine editor"""
    log = GetLogger(verbose=verbose)

    editor_dir = os.path.join(UE_ROOT, 'Engine', 'Binaries', 'Linux')
    if not os.path.isdir(editor_dir):
        raise IOError('No such directory {}'.format(editor_dir))

    project = os.path.join(INTPHYS_ROOT, 'intphys.uproject')
    if not os.path.isfile(project):
        raise IOError('No such file {}'.format(project))

    log.debug('running intphys in the Unreal Engine editor')

    command = './UE4Editor ' + project
    if standalone_game:
        command += ' -game'

    _Run(command, log, scenes_file, output_dir,
         seed=seed, dry=dry, resolution=resolution, cwd=editor_dir)


def FindDuplicates(directory):
    """Find any duplicated scenes in `directory`

    Having two identical scenes is very unlikely but was a problem
    while coding the '--njobs' option...

    Load and compare all 'params.json' files found in
    `directory`. Print duplicate on stdout.

    """
    # load all 'params.json' files in a dict: file -> content
    params = []
    for root, dirs, files in os.walk("./data"):
        for file in files:
            if file.endswith("params.json"):
                params.append(os.path.join(root, file))
    params = {p: json.load(open(p, 'r')) for p in params}

    # ensure each file have a different content (can't use
    # collections.Counter because dicts are unhashable)
    duplicate = []
    for i, (n1, p1) in enumerate(params.items()):
        for n2, p2 in params.items()[i+1:]:
            if p1 == p2:
                duplicate.append((n1, n2))

    if len(duplicate):
        print('WARNING: Found {} duplicated scenes.'.format(len(duplicate)))
        print('The following scenes are the same:')
        for (n1, n2) in sorted(duplicate):
            print('{}  ==  {}'.format(
                os.path.dirname(n1), os.path.dirname(n2)))


def CleanDataDirectory(directory):
    """Remove temporary and useless files and subdirs from `directory`

    This removes the *.t7 files, iterations_table.json and any empty
    subdirectory (containing nothing or only empty subdirectories).

    """
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for f in filenames:
            if f.endswith('.t7') or f == 'iterations_table.json':
                os.remove(os.path.join(dirpath, f))

        if not filenames and not sum([os.listdir(os.path.join(dirpath, d))
                                      for d in dirnames], []):
            # dirpath is empty or contains only empy subdirs
            shutil.rmtree(dirpath)


def AtExit(output_dir):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)


def Main():
    # parse command-line arguments
    args = ParseArgs()

    # setup an empty output directory
    dry_mode = False
    if args.output_dir is None:
        dry_mode = True
        output_dir = tempfile.mkdtemp()
        atexit.register(lambda: AtExit(output_dir))

    else:
        output_dir = os.path.abspath(args.output_dir)
        if os.path.exists(output_dir):
            if args.force:
                shutil.rmtree(output_dir)
            else:
                raise IOError(
                    'Existing output directory {}\n'
                    'Use the --force option to overwrite it'
                    .format(output_dir))
        os.makedirs(output_dir)

    # check the scenes_file is a correct JSON file
    try:
        json.load(open(args.scenes_file, 'r'))
    except ValueError:
        raise IOError(
              'The scenesuration is not a valid JSON file: {}'
              .format(args.scenes_file))

    # run the simulation either in the editor or as a standalone
    # program
    if args.editor:
        RunEditor(
            output_dir, args.scenes_file,
            seed=args.seed, dry=dry_mode, resolution=args.resolution,
            verbose=args.verbose)
    elif args.standalone_game:
        RunEditor(
            output_dir, args.scenes_file,
            seed=args.seed, dry=dry_mode, resolution=args.resolution,
            verbose=args.verbose, standalone_game=True)
    else:
        RunBinary(
            output_dir, args.scenes_file, njobs=1,  # args.njobs,
            seed=args.seed, dry=dry_mode, resolution=args.resolution,
            verbose=args.verbose)

    # check for duplicated scenes and warn if founded
    if not dry_mode:
        FindDuplicates(output_dir)

    # remove temporary files from the output directory
    CleanDataDirectory(output_dir)


if __name__ == '__main__':
    print(intphys_binaries())
    try:
        Main()
    except IOError as err:
        print('Fatal error, exiting: {}'.format(err))
        sys.exit(-1)
    except KeyboardInterrupt:
        print('Keyboard interruption, exiting')
        sys.exit(-1)
