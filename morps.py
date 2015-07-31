try:
    from osgeo import ogr
except ImportError:
    import ogr

import sys, subprocess, os

driverList = {"shp":"ESRI Shapefile","json":"GeoJSON","kml":"KML"}

### TO DO:
### Retain attribute information when creating new files

def unitConvert(un,deg):
    if un=="km":
        deg=deg/111.325
        return deg
    elif un=="mi":
        deg=deg/111.325
        deg=deg/.621371
        return deg
    elif un=="m":
        deg=deg/111.325
        deg=deg/1000
        return deg
    elif un=="ft":
        deg=deg/111.325
        deg=deg/.621371
        deg=deg/5280
        return deg
    elif un=="deg":
        return deg
    else:
        print "Inocorrect Units - distance will be in 'degrees'"
        return deg

def featureCount(inputFile,fileType="shp"):

    #return the number of features in a dataset
    driver = ogr.GetDriverByName(driverList[fileType])
    inputDS = driver.Open(inputFile,0)
    layer = inputDS.GetLayer()

    return layer.GetFeatureCount()


### This function creates a buffer for any file passed it, point, line, or
### polygon. It takes four arguments, InputFileName, for the file with which
### to create a buffer, OutFileName, which is the output file name, buf,
### which is specifying the size of the buffer, and fileType, which should be
### the type of the file being processed.
def buffer(InputFileName,OutFileName,buf,units,fileType="shp"):

    buf = unitConvert(units,buf)

    #get fields from input file
    inputFields = getFields(InputFileName,fileType)

    OutputFileName = OutFileName
    
    driver = ogr.GetDriverByName(driverList[fileType])
    inputDS = driver.Open(InputFileName, 0)
    if inputDS is None:
        print 'Could not open input file',InputFileName

    inputLayer = inputDS.GetLayer()

    if os.path.exists(OutputFileName):
        os.remove(OutputFileName)
    try:
        outputDS = driver.CreateDataSource(OutputFileName)  
    except:
        print 'Could not create output file',OutputFileName

    newLayer = outputDS.CreateLayer(OutputFileName, geom_type=ogr.wkbPolygon,srs=inputLayer.GetSpatialRef())
    if newLayer is None:
        print "Could not create layer for buffer in output data source"

    ##testing- add fields from input dataset to output dataset
    try:        
        for field in inputFields:
            fieldDefinition = ogr.FieldDefn(field,inputFields[field])

            #if field is type string
            if inputFields[field] == 4:
                fieldDefinition.setWidth(250)

            newLayer.CreateField(fieldDefinition)
    except:
        print 'ur fuct'

    newLayerDef = newLayer.GetLayerDefn()
    featureID = 0
    oldFeature = inputLayer.GetNextFeature()
    while oldFeature:

        geometry = oldFeature.GetGeometryRef()
        bufferz = geometry.Buffer(buf,5)
        try:
            newFeature = ogr.Feature(newLayerDef)
            newFeature.SetGeometry(bufferz)
            newFeature.SetFID(featureID)
            newLayer.CreateFeature(newFeature)
        except:
            print "Error adding buffer"

        newFeature.Destroy()
        oldFeature.Destroy()
        oldFeature = inputLayer.GetNextFeature()
        featureID += 1


    print 'There are', featureID, 'input features'

    inputDS.Destroy()
    outputDS.Destroy()

### This function creates centroids for any file passed to it
### It takes three arguments- inputFile, for the file with which
### to derive the centroids; outFile, which is the name of the new centroid
### file, and fileType, which is the type of file being passed (e.g., 'shp')
def centroid(inputFile,outFile,fileType="shp"):

    outputFileName = outFile

    driver = ogr.GetDriverByName(driverList[fileType])
    inputDS = ogr.Open(inputFile,0)

    if inputDS is None:
        print "Could not open input file", inputFile

    layer = inputDS.GetLayer()

    #test if input is point geometry
    if layer.GetGeomType() == 1:

        #exit the function! why are you getting centroids of points??
        return "You submitted a point dataset. Please submit a dataset containing line or polygon geometries."

    #create output file
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        outputDS = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output file', outputDS

    newLayer = outputDS.CreateLayer('centroid',geom_type=ogr.wkbPoint,srs=layer.GetSpatialRef())

    if newLayer is None:
        print "Couldn't create layer for buffer in output DS"

    newLayerDef = newLayer.GetLayerDefn()
    featureID = 0
    oldFeature = layer.GetNextFeature()
    
    while oldFeature:
        geometry = oldFeature.GetGeometryRef()
        centroid = geometry.Centroid()
        try:
            newFeature = ogr.Feature(newLayerDef)
            newFeature.SetGeometry(centroid)
            newFeature.SetFID(featureID)
            newLayer.CreateFeature(newFeature)
        except:
            print "Error computing centroid for feature", featureID

        newFeature.Destroy()
        oldFeature.Destroy()
        oldFeature = layer.GetNextFeature()
        featureID += 1

    inputDS.Destroy()
    outputDS.Destroy()

### This function checks two features in a file to see if one contains another.
### It takes 4 arguments, f1 for the first file, fid1 for the objectID of the
### first file's feature, f2 for the second file, fid2 for the objectID of the
### second file's feature. Returns whether the containment is True or False.
def contains(f1,f2,fid1=0,fid2=0,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Contains(geom2) == 1:
        return True
    else:
        return False

def difference(f1,f2,outFile,fileType="shp"):
    outputFileName = outFile
    
    driver = ogr.GetDriverByName(driverList[fileType])

    f1 = driver.Open(f1,0)
    layer1 = f1.GetLayer()
    feature1 = layer1.GetNextFeature()

    if f1 is None:
        print "Could not open file ", f1

    f2 = driver.Open(f2,0)
    layer2 = f2.GetLayer()
    feature2 = layer2.GetNextFeature()

    if f2 is None:
        print "Could not open file ", f2

    ### Create output file ###
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        output = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output datasource ', outputFileName

    newLayer = output.CreateLayer('SymmetricDifference',geom_type=ogr.wkbPolygon,srs=layer1.GetSpatialRef())

    if newLayer is None:
        print "Could not create output layer"

    newLayerDef = newLayer.GetLayerDefn()
    ##############################

    featureID = 0

    while feature1:

        layer2.ResetReading()
        geom1 = feature1.GetGeometryRef()
        feature2 = layer2.GetNextFeature()

        while feature2:

            geom2 = feature2.GetGeometryRef()
            
            if geom1.Overlaps(geom2) == 1:
                newgeom = geom1.Difference(geom2)
                newFeature = ogr.Feature(newLayerDef)
                newFeature.SetGeometry(newgeom)
                newFeature.SetFID(featureID)
                newLayer.CreateFeature(newFeature)
                featureID += 1
                newFeature.Destroy()
            
            else:
                newFeature1 = ogr.Feature(newLayerDef)
                newFeature1.SetGeometry(geom1)
                newFeature1.SetFID(featureID)
                newLayer.CreateFeature(newFeature1)

                featureID += 1
                newFeature2 = ogr.Feature(newLayerDef)
                newFeature2.SetGeometry(geom2)
                newFeature2.SetFID(featureID)
                newLayer.CreateFeature(newFeature2)
                featureID += 1
            
                newFeature1.Destroy()
                newFeature2.Destroy()
            
            feature2.Destroy()
            feature2 = layer2.GetNextFeature()
        
        feature1.Destroy()
        feature1 = layer1.GetNextFeature()
        
    f1.Destroy()
    f2.Destroy()
    print "Success"
    return

### This function checks two features in a file to see if one touches another.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether touch is True or False.
def disjoint(f1,f2,fid1=0,fid2=0,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Disjoint(geom2) == 0:
        return False
    else:
        return True

### This function returns the distance between two geometries.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's geometry, f2 for the second file, fid2 for the index of the
### second file's geometry.
def distance(f1,f2,fid1=0,fid2=0,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Distance(geom2) == -1:
        print 'An error occurred when attempting to compute the Distance'
        return geom1.Distance(geom2)
    else:
        return geom1.Distance(geom2)

### This function checks two features in a file to see their geometries are
### equal. It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's geometry, f2 for the second file, fid2 for the index of the
### second file's geometry. Returns a boolean depending on whether the geometries 
### are equal.
def equals(f1,f2,fid1=0,fid2=0,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Equals(geom2) == 1:
        return True
    else:
        return False

### This returns the bounding envelope for a specific geometry. See layerExtent.py
### to get the entire extent of a layer
def getEnvelope(inFile,g=0,fileType="shp"): #inFile = file, g = geometry
    driver = ogr.GetDriverByName(driverList[fileType])
    f = driver.Open(inFile,0)
    layer = f.GetLayer()

    featCount = layer.GetFeatureCount()

    if g > featCount:
        print "Feature ", g, "does not exist in", inFile

    try:
        feature = layer.GetFeature(g)
    
        geom = feature.GetGeometryRef()
        envelope = geom.GetEnvelope()
        return envelope

    except:
        print "Could not obtain envelope"

### This program returns all fields within a specific file. It takes one
### argument, f, for the name of the file with which the fields are desired
### to be known.
def getFields(f,fileType="shp"):

    driver = ogr.GetDriverByName(driverList[fileType])
    inFile = driver.Open(f,0)

    if inFile is None:
        print 'Could not open file', f, 'to read fields'

    layer = inFile.GetLayer()
    layerDefinition = layer.GetLayerDefn()

    fieldList = {}

    try:
        for i in range(layerDefinition.GetFieldCount()):
            fieldName = layerDefinition.GetFieldDefn(i).GetName()
            fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
            fieldList[fieldName] = fieldTypeCode

        return fieldList

    except:
        print "Unable to read fields from", f

### This function checks two features in a file to see if they intersect.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether the intersection is True or False.
def intersect(f1,f2,fid1=0,fid2=0,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Intersect(geom2) == 1:
        return True
    else:
        return False

### This returns the extent of the entire layer. See getEnvelope.py
### to get the bounding envelope for specific geometries
def layerExtent(f,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    f = driver.Open(f,0)
    layer = f.GetLayer()
    extent = layer.GetExtent()
    return extent

###tolerance: the distance tolerance for the simplification
def simplify(infile,outFile,tolerance, fileType="shp"):
    
    outFileName = outFile
    
    driver = ogr.GetDriverByName(driverList[fileType])
    infile = driver.Open(infile,0)

    if infile is None:
        print 'Could not open file ', infile
        sys.exit(1)

    oldLayer = infile.GetLayer()
    oldFeature = oldLayer.GetNextFeature()
    geom = oldFeature.GetGeometryRef()
    geomType = geom.GetGeometryType()

    ########Create output file############
    if os.path.exists(outFileName):
        os.remove(outFileName)

    try:
        output = driver.CreateDataSource(outFileName)
    except:
        print 'Could not create output file', outFileName
        sys.exit(1)

    newLayer = output.CreateLayer('Tolerance',geom_type=geomType,srs=oldLayer.GetSpatialRef())
    if newLayer is None:
        print 'Could not create layer for simplify in output file'
        sys.exit(1)

    newLayerDef = newLayer.GetLayerDefn()
    #######################################
    
    featureID = 0

    ####### Simplify geometry and add to output file #######
    while oldFeature:

        geometry = oldFeature.GetGeometryRef()
        simplifiedGeom = geometry.Simplify(tolerance)

        try:
            newFeature = ogr.Feature(newLayerDef)
            newFeature.SetGeometry(simplifiedGeom)
            newFeature.SetFID(featureID)
            newLayer.CreateFeature(newFeature)
        except:
            print "Error performing simplify"

        newFeature.Destroy()
        oldFeature.Destroy()
        oldFeature = oldLayer.GetNextFeature()
        featureID += 1
    ##########################################################

    infile.Destroy()
    output.Destroy()
    print "Success"
    return

def symmetricDifference(f1,f2,outFile,fileType="shp"):
    outputFileName = outFile
    
    driver = ogr.GetDriverByName(driverList[fileType])

    f1 = driver.Open(f1,0)
    layer1 = f1.GetLayer()
    feature1 = layer1.GetNextFeature()

    if f1 is None:
        print "Could not open file ", f1
        sys.exit(1)

    f2 = driver.Open(f2,0)
    layer2 = f2.GetLayer()
    feature2 = layer2.GetNextFeature()

    if f2 is None:
        print "Could not open file ", f2

    ### Create output file ###
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        output = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output datasource ', outputFileName
        sys.exit(1)

    newLayer = output.CreateLayer('SymmetricDifference',geom_type=ogr.wkbPolygon,srs=layer1.GetSpatialRef())

    if newLayer is None:
        print "Could not create output layer"
        sys.exit(1)

    newLayerDef = newLayer.GetLayerDefn()
    ##############################

    featureID = 0

    while feature1:

        layer2.ResetReading()
        geom1 = feature1.GetGeometryRef()
        feature2 = layer2.GetNextFeature()

        while feature2:

            geom2 = feature2.GetGeometryRef()
            
            if geom1.Overlaps(geom2) == 1:
                newgeom = geom1.SymmetricDifference(geom2)
                newFeature = ogr.Feature(newLayerDef)
                newFeature.SetGeometry(newgeom)
                newFeature.SetFID(featureID)
                newLayer.CreateFeature(newFeature)
                featureID += 1
                newFeature.Destroy()
            
            else:
                newFeature1 = ogr.Feature(newLayerDef)
                newFeature1.SetGeometry(geom1)
                newFeature1.SetFID(featureID)
                newLayer.CreateFeature(newFeature1)

                featureID += 1
                newFeature2 = ogr.Feature(newLayerDef)
                newFeature2.SetGeometry(geom2)
                newFeature2.SetFID(featureID)
                newLayer.CreateFeature(newFeature2)
                featureID += 1
            
                newFeature1.Destroy()
                newFeature2.Destroy()
            
            feature2.Destroy()
            feature2 = layer2.GetNextFeature()
        
        feature1.Destroy()
        feature1 = layer1.GetNextFeature()
        
    f1.Destroy()
    f2.Destroy()
    print "Success"
    return

### This program returns a list of all unique values within a specified
### field. It takes two arguments, 'f' for the filename (including extension)
### and 'field' for the desired field. Both arguments passed to the function
### should be strings.
def uniqueValues(f,field,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    inFile = driver.Open(f,0)
    layer = inFile.GetLayer()
    noExt = f[:-4]

    uniqueValues = "select distinct " + field + " from " + noExt
    
    result = inFile.ExecuteSQL(uniqueValues)
    resultFeat = result.GetNextFeature()

    uniqueFieldList = []
    
    while resultFeat:
        field = resultFeat.GetField(0)
        
        uniqueFieldList.append(field)

        resultFeat = result.GetNextFeature()

    print uniqueFieldList

### This function checks two features in a file to see if one is within another.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether the within is True or False.
def within(f1,f2,fid1=0,fid2=0, fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    if geom1.Within(geom2) == 1:
        return True
    else:
        return False
