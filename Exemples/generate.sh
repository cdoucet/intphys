#!/bin/bash

# abspath to the root directory of intphys
INTPHYS_DIR=$(dirname $(dirname $(readlink -f $0)))

cd $INTPHYS_DIR

mkdir -p data
rm -rf data/*

cat > data/to_generate.json <<EOF
{
 "scenario_O2" :
 {
   "test_visible" :
   {
     "static" : 1,
     "dynamic_1" : 1,
     "dynamic_2" : 1
   }
  }
}
EOF

for run in $(seq 1 1)
do
    ./intphys.py -g -o data/$run data/to_generate.json
done
