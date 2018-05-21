#!/bin/bash

function create_gif {
	mkdir temp
	for ((i=1;i<=100;i++));
	do
		j=""
		if [ $i -lt 100 ]; then
			j="0"
		fi
		if [ $i -lt 10 ]; then
			j="00"
		fi
		montage scene/scene_$j$i.png depth/depth_$j$i.png masks/masks_$j$i.png -tile x1 -geometry +0+0 temp/video_$j$i.png
		if [ $? -ne 0 ]; then
			echo "Something went wrong"
			rm -rf temp
			return 1
		fi
	done
	for ((i=101;i<=104;i++));
	do
		convert -size 864x288 xc:rgba\(0,0,0,255\) temp/video_$i.png
	done
	convert -delay 10 -loop 0 temp/video_*.png video.gif
	echo "created "$PWD"/video.gif"
	rm -rf temp
	return 0
}

function go_through {
for d in * ; do
		if [[ $d = "." || $d = ".." || ! -d $d ]]; then
			continue
	    elif [ $d = "depth" ]; then
			depth=${d}
		elif [ $d = "masks" ]; then
			masks=${d}
		elif [ $d = "scene" ]; then
			scene=${d}
		else
			cd $d
			go_through $1
		fi
		if [[ -d $depth && -d $masks && -d $scene ]]; then
			unset depth
			unset masks
			unset scene
			if [ "$#" = 1 ]; then
				rm video.gif
			else
				create_gif
				if [ $? = 1 ]; then
					return 1
				fi
			fi
		fi
	done
	cd ..
	return 0
}

if [ $# = 1 ]; then
	echo "Are you sure you want to delete the gifs ? y/n"
	read response
	if [ $response != "y" ]; then
		echo 1
	fi
fi
go_through $1
echo "over"
