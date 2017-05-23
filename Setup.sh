#!/bin/bash
#
# Copyright 2016, 2017 Mario Ynocente Castro, Mathieu Bernard
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
# This is the installation script of the NaivePhysics data generator
#

export NAIVEPHYSICS_ROOT=$(readlink -f .)
[ ! -f $NAIVEPHYSICS_ROOT/tools/build_package.sh ] \
    && echo "Error: ./tools/build_package.sh not found, are you in the NaivePhysics root directory?" \
    && exit 1

export UNREALENGINE_ROOT=$NAIVEPHYSICS_ROOT/UnrealEngine
TORCH_ROOT=$NAIVEPHYSICS_ROOT/torch


echo "Step 1: setup Torch and Lua"

git clone --branch master --depth 1 git@github.com:torch/distro.git $TORCH_ROOT
cd $TORCH_ROOT
bash install-deps
TORCH_LUA_VERSION=LUA52 ./install.sh -s
source $TORCH_ROOT/install/bin/torch-activate
luarocks install dkjson
luarocks install paths
luarocks install luaposix


echo "Step 2: setup Unreal Engine and UETorch"

# clone only branch 4.8 to save space and bandwidth
git clone --branch 4.8 --depth 1 git@github.com:EpicGames/UnrealEngine.git $UNREALENGINE_ROOT
cd $UNREALENGINE_ROOT

# clone and setup UETorch
git clone git@github.com:bootphon/UETorch.git Engine/Plugins/UETorch
Engine/Plugins/UETorch/Setup.sh

# clone and setup JSONQuery plugin
git clone https://github.com/marynate/JSONQuery_UE4.git Engine/Plugins/JSONQuery_UE4

# setup and compile Unreal Engine (this takes a while...)
./Setup.sh
./GenerateProjectFiles.sh
make

source $UNREALENGINE_ROOT/Engine/Plugins/UETorch/uetorch_activate.sh
cd $NAIVEPHYSICS_ROOT


echo "Step 3: write the activate-naivephysics script"
cat > activate-naivephysics << EOF
#!/bin/bash
#
# Setup environment to run the NaivePhysics project.
# Load torch and uetorch, update the Lua path.

export NAIVEPHYSICS_ROOT=$NAIVEPHYSICS_ROOT
export UNREALENGINE_ROOT=$UNREALENGINE_ROOT

source \$NAIVEPHYSICS_ROOT/torch/install/bin/torch-activate
source \$UNREALENGINE_ROOT/Engine/Plugins/UETorch/uetorch_activate.sh > /dev/null

LUA_PATH="\$NAIVEPHYSICS_ROOT/NaivePhysics/Scripts/?.lua;\$LUA_PATH"

export NAIVEPHYSICS_BINARY=\$NAIVEPHYSICS_ROOT/NaivePhysics/Package/LinuxNoEditor/NaivePhysics/Binaries/Linux/NaivePhysics
export NAIVEPHYSICS_PROJECT=\$NAIVEPHYSICS_ROOT/NaivePhysics/NaivePhysics.uproject

EOF


source $NAIVEPHYSICS_ROOT/activate-naivephysics

echo "Successful installation of the Unreal Engine with UETorch,
please package the NaivePhysics project within the UE editor (refer to
the 'Installation details' section of the README)"
