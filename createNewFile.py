import morps, ogr

inFields = morps.getFields(r"C:\GitHub\Morps\data\point.shp")

driver = ogr.GetDriverByName("ESRI Shapefile")

outputDS = driver.CreateDataSource(r"C:\GitHub\Morps\data\test.shp")

if outputDS is None:
    print 'is none'

newLayer = outputDS.CreateLayer(r"C:\GitHub\Morps\data\test.shp",geom_type=ogr.wkbPolygon)

if newLayer is None:
    print 'is also none'

for field in inFields:
    fieldDefinition = ogr.FieldDefn(inFields[field],ogr.OFTString)
    newLayer.CreateField(fieldDefinition)   
    
