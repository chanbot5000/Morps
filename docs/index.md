MORPS - Modifying Objects to Reduce Python Scripting
========

Python should be simple. Writing ~50 lines of code to create one buffer is not simple. 

Morps attempts to simplify geoprocessing with Python. Using the terminal/command line interface, navigate to the directory storing the morps.py file. 

Type 
    
    python 

to start the python shell and begin using morps

    import morps

    cities = "data/cities.shp"
	cities_buffered = "data/cities_buffered.shp"
	unit = 'miles'
	format = 'shp'

	morps.buffer(cities,cities_buffered,500,unit,format)

or even simpler

	morps.buffer("data/cities.shp","data/cities_buffered.shp","miles","shp")

Installation
========
>Note: This library is built on top of GDAL, and is required to be installed in order for MORPS to work correctly. [Find GDAL install instructions here.](https://www.mapbox.com/tilemill/docs/guides/gdal/) If you do not get errors when typing <b>import ogr</b> into the Python shell, you know that Python is configured and you are ready to use morps.

To install Morps, clone this repository or download the latest build from the [Python Package Index](https://pypi.python.org/pypi/Morps/0.1.4). Unzip the file and open the terminal (or Windows Command Shell) and cd into the directory. Type the following command to install:

    pip install .

If it installs with no errors, start the Python shell and attempt to import morps

    import morps

All right, lets Merk some Morps!

>Note: If you do not have pip installed (lookin' at you, Windows) you can install it by following [these instructions](https://pip.pypa.io/en/latest/installing.html#install-pip). If you get errors when typing pip into the command shell (after running get-pip.py) you may need to add pip to your %PATH% variable. 

>Windows users: To add pip to the %PATH% variable, open Control Panel > System and Security > System > Advanced System Settings > Environment Variables > Under "System Variables" scroll down to 'Path', click it and then click edit. Add the following text to the end of the Variable Value: ;C:\Path\To\Python\Scripts  where \Path\To\Python is the directory path to your local install of Python. It may look something like C:\Python27 or if you are an ArcGIS user it could look like C:\Python27\ArcGIS10.x\ and then you need to reference the Scripts folder inside the Python install directory, because that is where pip is stored. Also, it is imperative that a semi-colon is used to separate variables.

Geoprocessing Supported by Morps
========

* Buffer
* Contains
* Difference
* Disjoint
* Distance
* Equals
* Find Centroid
* Feature Count
* Get Feature Envelope
* Get Fields
* Get Layer Extent
* Get Unique Values
* Intersect
* Simplify
* Symmetric Difference
* Within

The code in this repo is also intended to demonstrate how one could utilize the OGR vector library within GDAL 
for performing basic geoprocessing tasks.


Other useful online resources for GDAL:

<ul>
<li>Geoprocessing with Python using Open Source GIS- http://www.gis.usu.edu/~chrisg/python/2009/</li>
<li>GDAL Homepage- http://www.gdal.org/index.html</li>
<li>OGR Classlist- http://www.gdal.org/ogr/annotated.html</li>
<li>OGR Hierarchy, super useful for understanding geometry features- http://www.gdal.org/ogr/hierarchy.html</li>
<li>OGR2OGR Cheatsheet- http://www.bostongis.com/PrinterFriendly.aspx?content_name=ogr_cheatsheet</li>
<li>Converting spatial data using OGR2OGR- http://giscollective.org/#/spatial-data-conversion-using-python/</li>
</ul>
