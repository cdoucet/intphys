#!/bin/bash
#
# Run this script from the Tools directory of the intphys project to
# build all the shaders and assets used in the game. From
# https://docs.unrealengine.com/latest/INT/Engine/Basics/DerivedDataCache/index.html

# abspath to the root directory of intphys
INTPHYS_DIR=$(readlink -f ..)

$UE_ROOT/Engine/Binaries/Linux/UE4Editor $INTPHYS_DIR/intphys.uproject -run=DerivedDataCache -fill
