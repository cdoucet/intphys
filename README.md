# intphys #

#### Data generation for the Intuitive Physics Challenge - http://www.intphys.com ####

Developed with
[Unreal Engine](https://www.unrealengine.com/what-is-unreal-engine-4)
4.8 and our [UETorch](https://github.com/bootphon/UETorch) fork.


## Video exemples ##


#### Train samples ####

Train samples are always physically possible and have high variability

<img src="exemples/gif/train_1.gif" width="150"> <img src="exemples/gif/train_2.gif" width="150"> <img src="exemples/gif/train_3.gif" width="150"> <img src="exemples/gif/train_4.gif" width="150">


#### Test samples ####

Test samples have a constrained variability and come as quadruplets: 2
possibles cases and 2 impossibles ones

<img src="exemples/gif/test_1.gif" width="150"> <img src="exemples/gif/test_2.gif" width="150"> <img src="exemples/gif/test_3.gif" width="150"> <img src="exemples/gif/test_4.gif" width="150">


#### Metadata ####

Each video comes with it's associated depth field and object masking
(each object have a unique id), along with a detailed status in JSON
format.

<img src="exemples/gif/meta_1.gif" width="150"> <img src="exemples/gif/meta_2.gif" width="150"> <img src="exemples/gif/meta_3.gif" width="150">


## Installation details ##

This installation process succeeded on Debian stable (Jessie) and
Ubuntu 14.04. It may be fine for other Unices as well, but this have
not been tested.

* First of all setup an Epic Games account at
  https://github.com/EpicGames/Signup/, needed to clone the Unreal
  Engine repository from github. UETorch currently only works with the
  source distribution of UE4 in the version 4.8, not the binary
  download.


* The clone the NaivePhysics repository from github, go in its root
  directory and run the `Setup.sh` script:

        git clone git@github.com:bootphon/NaivePhysics.git
        cd NaivePhysics
        ./Setup.sh

  This takes a while: it downloads and installs Lua, Torch, Unreal
  Engine and UETorch in the `NaivePhysics` directory. It finally
  generates a `activate-naivephysics` script that load the project
  environment.

* **Note for Ubuntu 16.04 users** The install is not working out of
  the box because UE-4.8 was made for Ubuntu 14.04. Two problems to solve:

    - in the file
      `NaivePhysics/UnrealEngine/Engine/Build/BatchFiles/Linux/Setup.sh`
      suppress the line 44 "libmono-corlib4.0-cil" and replace it by
      "mono-reference-assemblies-4.0 mono-devel"

    - ensure you are using clang-3.5 (the default is clang-3.8). A
      dirty but simple way to do that is `sudo apt-get remove clang`
      and then `sudo apt-get install clang-3.5` (you can make the
      reverse operation after).

* The NaivePhysics main executable is a Python script relying on
  (joblib)[https://pythonhosted.org/joblib] to run
  sub-processes. Install it, for exemple using pip:

        [sudo] pip install joblib


* The final step is to package the
  `NaivePhysics/NaivePhysics.uproject` project into a standalone
  binary. You need a manual intervention in the editor. Open it with:

        ./naivedata.py exemple.json --editor --verbose

  Answer *yes* if a pop-up asks you for rebuilding missing libraries.

  In the *File/Package Project* menu, select the *Linux* target and
  `./NaivePhysics/Package` as the package directory. This operation
  takes a while on the first time.

  ![Packaging menu](https://docs.unrealengine.com/latest/images/Engine/Basics/Projects/Packaging/packaging_menu.jpg)


* **Potential issue:** If the 3D scene generated seems to be frozen
  (the spheres are moving but the wall remains in the 'down' position
  for a while), there is a problem with the packaged binary.

  Try to repackage it within the UnrealEngine editor.

  If the problem persists, launch the editor (with the *--editor*
  option of `naivedata.py`), click on the *Play* button (in the top
  panel) and, then, repackage the game.


## Usage ##

* Go in your `NaivePhysics` directory and run:

        source activate-naivephysics

* Then use the `naivedata.py` program to generate data. To discover
  the arguments, have a:

        ./naivedata.py --help

* The basic usage is calling `naivedata.py config.json -o
  ./output_data`. This reads the scenes to be generated from the
  `config.json` file and write them in the folder `./output_data`.


## Additional utils ##

In the `tools` directory are stored few utility scripts:

* **images2video.sh** : converts a sequence of images into a video or
  a gif file. Used to postprocess the generated png images.

* **clean.sh** : deletes the NaivePhysics build/binaries directories.

* **build_package.sh** : builds the NaivePhysics project as a
  standalone binary program. *Outdated, the prefered way to package
  the game is using the editor*.


## License ##

**Copyright 2016, 2017 Mario Ynocente Castro, Mathieu Bernard**


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
