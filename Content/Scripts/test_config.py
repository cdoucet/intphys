#!/usr/bin/python3

import configuration

json_file = '/home/mathieu/dev/intphys/Exemples/exemple.json'

config = configuration.Configuration(json_file, '/tmp')

for it in config.iterations:
    print(it)
