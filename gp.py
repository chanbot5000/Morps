try:
    from osgeo import ogr
except ImportError:
    import ogr

import sys, subprocess, os

driverList = {"shp":"ESRI Shapefile","json":"GeoJSON","kml":"KML"}

### This function appends the data from one file to another. It takes three
### arguments, f1 and f2, which should be the files used for appending, and 
### fileType, which should be the type of the files being processed (e.g., 'shp').
def append(f1,f2,fileType="shp"):
    
    noExt = f1[:-4]
    subprocess.call(["ogr2ogr","-f",driverList[fileType],"-append","-nln",noExt,f1,f2,"-update"])

### This function creates a buffer for any file passed it, point, line, or
### polygon. It takes four arguments, InputFileName, for the file with which
### to create a buffer, OutFileName, which is the output file name, buf,
### which is specifying the size of the buffer, and fileType, which should be
### the type of the file being processed.
def buffer(InputFileName,OutFileName,buf,fileType="shp"):

    OutputFileName = OutFileName
    
    #driver = ogr.GetDriverByName('ESRI Shapefile')
    driver = ogr.GetDriverByName(driverList[fileType])
    inputDS = driver.Open(InputFileName, 0)
    if inputDS is None:
        print 'Could not open input file',InputFileName
        sys.exit(1)

    inputLayer = inputDS.GetLayer()

    if os.path.exists(OutputFileName):
        os.remove(OutputFileName)
    try:
        outputDS = driver.CreateDataSource(OutputFileName)
    except:
        print 'Could not create output file',OutputFileName
        sys.exit(1)

    newLayer = outputDS.CreateLayer('TestBuffer', geom_type=ogr.wkbPolygon,srs=inputLayer.GetSpatialRef())
    if newLayer is None:
        print "couldn't create layer for buffer in output DS"
        sys.exit(1)

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
            print "error adding buff"

        newFeature.Destroy()
        oldFeature.Destroy()
        oldFeature = inputLayer.GetNextFeature()
        featureID += 1


    print 'There are ', featureID, ' input features'

    inputDS.Destroy()
    outputDS.Destroy()

### This function creates centroids for any file passed to it
### It takes three arguments- inputFile, for the file with which
### to derive the centroids; outFile, which is the name of the new centroid
### file, and fileType, which is the type of file being passed (e.g., 'shp')
def centroid(inputFile, outFile, fileType="shp"):

    outputFileName = outFile

    driver = ogr.GetDriverByName(driverList[fileType])
    inputDS = ogr.Open(inputFile,0)

    if inputDS is None:
        print "Could not open input file", inputFile
        sys.exit(1)

    layer = inputDS.GetLayer()

    #create output file
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        outputDS = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output file', outputDS
        sys.exit(1)

    newLayer = outputDS.CreateLayer('centroid',geom_type=ogr.wkbPoint,srs=layer.GetSpatialRef())

    if newLayer is None:
        print "Couldn't create layer for buffer in output DS"
        sys.exit(1)

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
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether the containment is True or False.
def contains(f1,fid1,f2,fid2,fileType="shp"):
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
        print "CONTAINMENT IS TRUE"
    else:
        print "CONTAINMENT IS FALSE"

def difference(f1,f2,outFile, fileType="shp"):
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
   # feature2 = layer2.GetNextFeature()

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
                newLayer.CreateFeature(newfeature2)
                featureID += 1
            
                newFeature1.Destroy()
                newFeature2.Destroy()
            
            feature2.Destroy()
            feature2 = layer2.GetNextFeature()
        
        feature1.Destroy()
        feature1 = layer1.GetNextFeature()
        
    f1.Destroy()
    f2.Destroy()

### This function checks two features in a file to see if one touches another.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether touch is True or False.
def disjoint(f1,fid1,f2,fid2, fileType="shp"):
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
        print f1 + "'S FEATURE", fid1, "IS NOT DISJOINT WITH", f2 + "'S FEATURE", fid2
    else:
        print f1 + "'S FEATURE", fid1, "IS DISJOINT WITH",f2 + "'S FEATURE", fid2

### This function returns the distance between two geometries.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's geometry, f2 for the second file, fid2 for the index of the
### second file's geometry.
def distance(f1,fid1,f2,fid2, fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    
    file1 = driver.Open(f1,0)
    layer1 = file1.GetLayer()
    feat1 = layer1.GetFeature(fid1)
    geom1 = feat1.GetGeometryRef()

    file2 = driver.Open(f2,0)
    layer2 = file2.GetLayer()
    feat2 = layer2.GetFeature(fid2)
    geom2 = feat2.GetGeometryRef()

    return geom1.Distance(geom2)

### This function checks two features in a file to see their geometries are
### equal. It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's geometry, f2 for the second file, fid2 for the index of the
### second file's geometry. Returns a boolean depending on whether the geometries 
### are equal.
def equals(f1,fid1,f2,fid2, fileType="shp"):
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
        print "GEOMETRIES ARE EQUAL"
    else:
        print "GEOMETRIES ARE EQUAL"

### This returns the bounding envelope for a specific geometry. See layerExtent.py
### to get the entire extent of a layer
def getEnvelope(inFile,g,fileType="shp"): #inFile = file, g = geometry
    driver = ogr.GetDriverByName(driverList[fileType])
    f = driver.Open(inFile,0)
    layer = f.GetLayer()

    featCount = layer.GetFeatureCount()

    if g > featCount:
        print "Feature ", g, "does not exist in", inFile
        sys.exit(1)

    try:
        feature = layer.GetFeature(g)
    
        geom = feature.GetGeometryRef()
        envelope = geom.GetEnvelope()
        return envelope

    except:
        print "Could not obtain envelope"
        sys.exit(1)

### This program returns all fields within a specific file. It takes one
### argument, f, for the name of the file with which the fields are desired
### to be known.
def getFields(f,fileType="shp"):

    driver = ogr.GetDriverByName(driverList[fileType])
    inFile = driver.Open(f,0)

    if inFile is None:
        print 'Could not open file', f, 'to read fields'
        sys.exit(1)

    layer = inFile.GetLayer()
    feat = layer.GetNextFeature()
    featDefn = feat.GetDefnRef()
    
    fieldCount = feat.GetFieldCount()

    try:
        i = 0
        while i < fieldCount:
            fieldDefn = featDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetNameRef()
            print fieldName
            i += 1

    except:
        print "Unable to read fields from", f

### This function checks two features in a file to see if they intersect.
### It takes 4 arguments, f1 for the first file, fid1 for the index of the
### first file's feature, f2 for the second file, fid2 for the index of the
### second file's feature. Returns whether the intersection is True or False.
def intersect(f1,fid1,f2,fid2,fileType="shp"):
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
        print "INTERSECTION IS TRUE"
    else:
        print "INTERSECTION IS FALSE"

### This returns the extent of the entire layer. See getEnvelope.py
### to get the bounding envelope for specific geometries
def layerExtent(f,fileType="shp"):
    driver = ogr.GetDriverByName(driverList[fileType])
    f = driver.Open(f,0)
    layer = f.GetLayer()
    extent = layer.GetExtent()
    return extent

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
   # feature2 = layer2.GetNextFeature()

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
                newLayer.CreateFeature(newfeature2)
                featureID += 1
            
                newFeature1.Destroy()
                newFeature2.Destroy()
            
            feature2.Destroy()
            feature2 = layer2.GetNextFeature()
        
        feature1.Destroy()
        feature1 = layer1.GetNextFeature()
        
    f1.Destroy()
    f2.Destroy()

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
def within(f1,fid1,f2,fid2, fileType="shp"):
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
        print f1, "IS WITHIN", f2
    else:
        print f1, "IS NOT WITHIN", f2