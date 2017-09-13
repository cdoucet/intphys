#!/bin/bash
#
# Copyright 2017 CoML team - ENS, INRIA, EHESS, CNRS
#
# You can redistribute this file and/or modify it under the terms of
# the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#
# This is the installation script of the intphys data generator
#


# check Unreal Engine is here
[ -z UNREALENGINE_ROOT ] \
    && echo "Error: $UNREALENGINE_ROOT is not defined, please define this environment variable to the root directory of your UnrealEngine installation (eg. 'UNREALENGINE_ROOT=/path/to/UnrealEngine ./setup.sh')" \
    && exit 1


export INTPHYS_ROOT=$(readlink -f .)
[ ! -f $INTPHYS_ROOT/setup.sh ] \
    && echo "Error: ./setup.sh not found, are you in the intphys directory?" \
    && exit 1

# # clone and setup UnrealEngine (clone only one branch and no history
# # to save resources)
# export UNREALENGINE_ROOT=$INTPHYS_ROOT/UnrealEngine
# git clone --branch 4.17 git@github.com:EpicGames/UnrealEngine.git $UNREALENGINE_ROOT
# cd $UNREALENGINE_ROOT
# ./Setup.sh
# ./GenerateProjectFiles.sh
# make
