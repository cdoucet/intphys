# building an html page from gif files
html: data
	./build_html.sh $< $@

# generate data in gif and avi from config file
data: config.json
	$(NAIVEPHYSICS_ROOT)/naivedata.py $< $@ -f
	$(NAIVEPHYSICS_ROOT)/tools/images2video.sh $@ gif

clean:
	rm -rf html data
