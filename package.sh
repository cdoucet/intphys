#!/bin/bash

PACKAGE_DIR=$(readlink -f ./Package)
mkdir -p $PACKAGE_DIR

cd $UE_ROOT/Engine/Build/BatchFiles/

# ./RunUAT.sh BuildCookRun -project=/home/mathieu/lscp/dev/intphys/intphys.uproject \
#             -noP4 -platform=Linux -clientconfig=Development -serverconfig=Development \
#             -cook -allmaps -build -stage -pak -archive -archivedirectory="$PACKAGE_DIR"


cd ../../Binaries/DotNET/

mono AutomationTool.exe \
     -ScriptsForProject=/home/mathieu/lscp/dev/intphys/intphys.uproject \
     BuildCookRun -nocompileeditor -nop4 \
     -project=/home/mathieu/lscp/dev/intphys/intphys.uproject -cook -stage \
     -archive -archivedirectory=/home/mathieu/lscp/dev/intphys/Package/ \
     -package -clientconfig=Development -ue4exe=UE4Editor -pak -prereqs \
     -nodebuginfo -targetplatform=Linux -build -utf8output
