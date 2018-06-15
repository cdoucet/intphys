#!/bin/bash

function create_gif {
	first=${1##*/}_
	second=${2##*/}_
	truc=001
	size="$(identify -format '%w' $1/${first}001.png)"
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
		montage $1/$first$j$i.png $2/$second$j$i.png -tile x1 -geometry +0+0 temp/video_$j$i.png
		if [ $? -ne 0 ]; then
			echo "Something went wrong"
			rm -rf temp
			return 1
		fi
	done
	for ((i=101;i<=104;i++));
	do
		convert -size $(($size*2))x$size xc:rgba\(0,0,0,255\) temp/video_$i.png
	done
	convert -delay 10 -loop 0 temp/video_*.png video.gif
	echo "created "$PWD"/video.gif"
	rm -rf temp
	return 0
}

if [ $# -ne 2 ]; then
	echo "You must specify 2 directories containing 100 pictures each"
	exit 1
fi

create_gif $1 $2
echo "over"
