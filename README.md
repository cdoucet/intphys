# intphys-2.0 #

#### Data generation for the Intuitive Physics Challenge - http://www.intphys.com ####

Developed with
[Unreal Engine](https://www.unrealengine.com/what-is-unreal-engine-4)
4.17 and the [UnrealEnginePython](https://github.com/20tab/UnrealEnginePython)
plugin.

The 2.0 version of intphys is a reimplementation of intphys-1.0 based on UE-4.17 (was
UE-4.8) using the Python scripting language (was Lua).


## Video exemples ##

#### Train samples ####

Train samples are always physically possible and have high variability

<img src="Exemples/gif/train_1.gif" width="150"> <img src="Exemples/gif/train_2.gif" width="150"> <img src="Exemples/gif/train_3.gif" width="150"> <img src="Exemples/gif/train_4.gif" width="150">


#### Test samples ####

Test samples have a constrained variability and come as quadruplets: 2
possibles cases and 2 impossibles ones

<img src="Exemples/gif/test_1.gif" width="150"> <img src="Exemples/gif/test_2.gif" width="150"> <img src="Exemples/gif/test_3.gif" width="150"> <img src="Exemples/gif/test_4.gif" width="150">


#### Metadata ####

Each video comes with it's associated depth field and object masking
(each object have a unique id), along with a detailed status in JSON
format.

<img src="Exemples/gif/meta_1.gif" width="150"> <img src="Exemples/gif/meta_2.gif" width="150"> <img src="Exemples/gif/meta_3.gif" width="150">


## Installation details ##

This installation process succeeded on Debian stable (Jessie) and
Ubuntu 16.04. It may be fine for other Unices as well, but this have
not been tested.

* First of all setup an Epic Games account at
  https://github.com/EpicGames/Signup/, needed to clone the Unreal
  Engine repository from github. The version 4.17 of Unreal Engine is
  recommended but any version supported by UnrealEnginePython should
  work (from 4.12 to 4.17).

* Install Unreal Engine on your machine. We define the installation
  directory, configure and compile it. This takes a while.

        UNREALENGINE_ROOT=~/dev/UnrealEngine  # change to whatever you like
        git clone --branch 4.17 git@github.com:EpicGames/UnrealEngine.git $UNREALENGINE_ROOT
        cd $UNREALENGINE_ROOT
        ./Setup.sh
        ./GenerateProjectFiles.sh
        make

* Install intphys. Clone the repository and its dependancies
  from github, go in its root directory and run the `setup.sh` script:

        git clone --recursive git@github.com:bootphon/intphys.git

* The intphys main executable is a Python script relying
  on [joblib](https://pythonhosted.org/joblib) to run
  sub-processes. Install it, for exemple using pip:

        [sudo] pip install joblib


* The final step is to package the `intphys/intphys.uproject` project
  into a standalone binary. You need a manual intervention in the
  editor. Open it with:

        ./naivedata.py exemple.json --editor --verbose

  * Answer *no* if a pop-up complains the UnrealEnginePython plugin is
    not compatible with the current engine version.

  * Answer *yes* if a pop-up asks you for rebuilding missing libraries.

  In the *File/Package Project* menu, select the *Linux* target and
  `./intphys/Package` as the package directory. This operation takes a
  while on the first time.

  ![Packaging menu](https://docs.unrealengine.com/latest/images/Engine/Basics/Projects/Packaging/packaging_menu.jpg)


* **Potential issue:** If the 3D scene generated seems to be frozen
  (the spheres are moving but the wall remains in the 'down' position
  for a while), there is a problem with the packaged binary.

  Try to repackage it within the UnrealEngine editor.

  If the problem persists, launch the editor (with the *--editor*
  option of `intphysdata.py`), click on the *Play* button (in the top
  panel) and, then, repackage the game.


## Usage ##

* Go in your `intphys` directory and run:

        source activate-intphys

* Then use the `naivedata.py` program to generate data. To discover
  the arguments, have a:

        ./intphysdata.py --help

* The basic usage is calling `intphysdata.py config.json -o
  ./output_data`. This reads the scenes to be generated from the
  `config.json` file and write them in the folder `./output_data`.


## Additional utils ##

In the `Tools` directory are stored few utility scripts:

* **images2video.sh** : converts a sequence of images into a video or
  a gif file. Used to postprocess the generated png images.

* **clean.sh** : deletes the intphys build/binaries directories.

In the `Exemples` directory are stored scripts to generate few videos,
extract them to gif pictures and embeed them in a html page.
