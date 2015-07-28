===========
Morps - Modifying Objects to Reduce Python Scripting
===========

Python should be simple. Writing ~50 lines of code to create one buffer is not simple. 

Morps attempts to simplify geoprocessing with Python. Using the terminal/command line interface, navigate to the directory storing the morps.py file. 

to start the python shell and begin using morps::

    from morps import morps

    cities = "data/cities.shp"
	cities_buffered = "data/cities_buffered.shp"
	unit = 'miles'
	format = 'shp'

	morps.buffer(cities,cities_buffered,500,unit,format)

or even simpler::

	morps.buffer("data/cities.shp","data/cities_buffered.shp","miles","shp")

This library is built on top of GDAL, and is required to be installed in order for MORPS to work correctly. Find GDAL install instructions here- https://www.mapbox.com/tilemill/docs/guides/gdal/

If you do not get errors when typing <b>import ogr</b> into the Python shell, you know that Python is configured and you are ready to use morps.

The code in this repo is also intended to demonstrate how one could utilize the OGR vector library within GDAL 
for performing basic geoprocessing tasks.

