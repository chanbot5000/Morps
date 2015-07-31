## Buffer

Used to create a buffer for any point, line, or polygon file. Currently no attribute information is carried over into the output file (working on it!).

**Creation**

    buffer(input file, output file, buffer distance, units, file type)

**Arguments**

Argument | Type | Description
--- | --- | ---
input file | string | File to be buffered. Supported types are .shp, .geojson, and .kml
output file | string | File containing results of the buffer geoprocess. Will be the same output file type as input file
buffer distance | int | Size of buffer in specified units
units | string | What units with which to calculate the buffer. Currently accepts *km*,*mi*,*m*,*ft*, and *deg*
file type | string | *Optional:*  specify type of file. Currently accepts *shp*,*json*, and *kml* as string arguments. Defaults to *shp* if no argument is passed. 

**Code Sample**
    
    import morps

	cities = "data/cities.shp"
	cities_buffered = "data/cities_buffered.shp"
	buffer_distance = 500
	units = 'mi'
	format = 'shp'

	morps.buffer(cities,cities_buffered,buffer_distance,units,format)

---

## Centroid

Creates a new file containing the centroids of any line or polygon file. Currently no attribute information is carried over into the output file (working on it!).

**Creation**

    centroid(input file, output file, file type)

**Arguments**

Argument | Type | Description
--- | --- | ---
input file | string | File used to generate centroids. Supported types are .shp, .geojson, and .kml
output file | string | File containing results of the centroid process. Will be the same output file type as input file
file type | string | *Optional:*  specify type of file. Currently accepts *shp*,*json*, and *kml* as string arguments. Defaults to *shp* if no argument is passed. 

**Code Sample**
    
    import morps

	parks = "data/parks.shp"
	park_centroids = "data/park_centroids.shp"
	format = 'shp'

	morps.centroid(parks,park_centroids,format)