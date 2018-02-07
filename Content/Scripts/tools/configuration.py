"""Load of the scenes file and setup the iterations it includes.

Translates the scenes file (from JSON) into a list of iterations to
render. Each scenario can be composed of several iterations (train
scenarii have a single iteration, test ones have 4 iterations plus
additionnal checks).

An `iteration` is a table with the following fields:
  iteration.id is the index of the iteration in the table
  iteration.type is -1 for train and >0 for testing
  iteration.block is the block for that iteration
  iteration.path is the output directory for that iteration

"""

# TODO make a class Iteration.
# TODO Once block classes are implemeted, link
# them to here (for occlusion checks size and so on...)

import json
import os

class Configuration(object):
    def __init__(self, json_file, output_dir):
        self.nruns_train = 0
        self.nruns_test = 0
        self.current_iteration = 0
        self.iterations = []

        # loading the JSON file
        raw_json = json.loads(open(json_file, 'r').read())

        # build the iterations list from the JSON (this populates
        # self.{iterations, nruns_train, nruns_test})
        self._parse_config_file(raw_json)

        # now that we know the total number of iterations, we add the
        # path were the screenshots are metadata will be stored.
        for iteration in self.iterations:
            self._set_iteration_path(iteration, output_dir)

    def get_current_iteration(self):
        return self.iterations[self.current_iteration]

    def _parse_config_file(self, raw_json):
        # iterate on the blocks defined in the configuration
        for block_name, block_cases in raw_json.items():
            for k, v in block_cases.items():
                if 'train' in k:
                    self._add_train_iteration(block_name, k, v)
                else:
                    self._add_test_iteration(block_name, k, v)

    def _add_train_iteration(self, block, case, nruns):
        name = block
        if case:
            name += '.' + case

        for i in range(1, nruns + 1):
            self.nruns_train += 1
            self._add_iteration(name, -1, self.nruns_train)

    def _add_test_iteration(self, block, case, subblocks):
        for subblock, nruns in subblocks.items():
            name = block + '.' + case + '_' + subblock
            nsubiterations = 4 + self._get_nocclusion_checks(name)

            if isinstance(nruns, dict):
                # the number of actors is specified
                for nactors, nruns_2 in nruns.items():
                    self.nruns_test += 1
                    for t in range(nsubiterations, 0, -1):
                        self._add_iteration(name, t, self.nruns_test, int(nactors))
            else:
                # nruns is an integer: random nactors in each scene
                for i in range(1, nruns + 1):
                    self.nruns_test += 1
                    for t in range(nsubiterations, 0, -1):
                        self._add_iteration(name, t, self.nruns_test)

    def _add_iteration(self, block, type, id, nactors=None):
        """Add a new iteration in the iterations list to be rendered"""
        iteration = {'block': block, 'type': type, 'id': id}
        if nactors:
            iteration['nactors'] = nactors

        self.iterations.append(iteration)

    @staticmethod
    def _get_nocclusion_checks(name):
        # TODO should be retrieved from block classes
        size = 0
        if 'visible' in name or 'train' in name:
            size = 0
        elif name.endswith('2'):
            size = 2
        else:
            size = 1

        # block O2 has twice the checks of block O1
        if 'O2' in name:
            size *= 2

        return size

    def _set_iteration_path(self, iteration, output_dir):
        id_padded = '0' * (len(str(self.nruns_test + self.nruns_train)) -
                           len(str(iteration['id']))) + str(iteration['id'])

        iteration['path'] = os.path.join(
            output_dir,
            'train' if 'train' in iteration['block'] else 'test',
            id_padded + '_' + iteration['block'].replace('.', '_'))

        if 'train' not in iteration['block']:
            iteration['path'] = os.path.join(
                iteration['path'], str(iteration['type']))
