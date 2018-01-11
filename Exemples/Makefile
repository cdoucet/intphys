COMPRESS_GIF_OPTIONS="-compress jpeg -resize 128x128"

# building an html page from gif files
html: data gif
	./build_html.sh $< $@

# generate data as raw png files
data: config.json
	../intphys.py $< $@ -f

# generate compressed gifs from raw png
gif: data
	../Tools/images2video.sh $< $@ $(COMPRESS_GIF_OPTIONS)

clean:
	rm -rf html data
