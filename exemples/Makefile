COMPRESS_GIF_OPTIONS="-compress jpeg -resize 128x128"

# building an html page from gif files
html: data gif
	./build_html.sh $< $@

# generate data as raw png files
data: config.json
	$(NAIVEPHYSICS_ROOT)/naivedata.py $< $@ -f

# generate compressed gifs from raw png
gif: data
	$(NAIVEPHYSICS_ROOT)/tools/images2video.sh $< $@ $(COMPRESS_GIF_OPTIONS)

clean:
	rm -rf html data
