# coding: utf-8
from collections import namedtuple
import json
import os
import pandas as pd
import numpy as np
import matplotlib.path as pathtools
import shapefile

def main():
    print('Ran main')    

def shapefileGrid(inputShp,degStep=0.005,makeShpFile=True,return_data=False):
    gridData = gridDataGen(inputShp,degStep)
    if makeShpFile:
        center = makeShapeFile(gridData)
        if return_data:
            return gridData
    else:
        if return_data:
            return gridData    

#TODO:
# - Get rid of pyshp, use Fiona(json shapefiles), convert shp to json using shp2Geojson?

###########################################################
# REMEMBER it's (Lat,Lon) or (y,x), not (Lon,Lat) or (x,y)#
###########################################################

# Martin Lolux http://geospatialpython.com/2013/07/shapefile-to-geojson.html
def shp2GeoJson(filename):
    root,ext = os.path.splitext(filename)
    # read the shapefile
    reader = shapefile.Reader(filename)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature",geometry=geom, properties=atr)) 
   
    # write the GeoJSON file
    geojson = open(root+'.json', "w")
    geojson.write(json.dumps({"type": "FeatureCollection",
    "features": buffer}, indent=2) + "\n")
    geojson.close()

# Make a Grid with Spherical Coordinates (N,2) Array
def makeGrid(latlim,lonlim,degStep):
    # Make Sure the Grid is less than 10,000 Points
    def checkSize(latlim,lonlim,degStep):
        a = np.arange(latlim[0],latlim[1],degStep).size
        b = np.arange(lonlim[0],lonlim[1],degStep).size
        grid_size = a*b
        return grid_size
    
    grid_size = checkSize(latlim,lonlim,degStep)
    while grid_size > 20e3:
        degStep = 1.1*degStep
        grid_size = checkSize(latlim,lonlim,degStep)
    
    # Create Grid Points
    lat, lon = np.mgrid[latlim[0]:latlim[1]:degStep,
        lonlim[0]:lonlim[1]:degStep]
    grid = np.column_stack((lat.reshape(lat.size,1),
        lon.reshape(lon.size,1)))
    return grid,degStep

def gridDataGen(inputShp,degStep=0.01):
    # If input is .shp, convert to json
    rootname,ext = inputShp.split('.')
    if ext == 'shp':
        shp2GeoJson(inputShp)
        inputShp = rootname + '.json'
    
    # Read the GeoJson File into an Array
    with open(inputShp) as data_file:    
        jsonArray = json.load(data_file)

    # Get the coordinates from the Array
    pathpts = np.array(jsonArray['features'][0]['geometry']['coordinates'][0])
    
    # Shape Files are Lon,Lat so we need to flip these
    pathpts[:,[0, 1]] = pathpts[:,[1, 0]]
    
    # Create a Path from the coordinates
    path = pathtools.Path(pathpts,closed=True)

    # Get the Bounding Box limits of the Shape
    lims = path.get_extents().get_points()
    latlim = lims[:,0]
    lonlim = lims[:,1]
    center = [np.mean(latlim),np.mean(lonlim)]

    # Create the Grid  
    grid,degStep = makeGrid(latlim,lonlim,degStep)
    
    # Find index of Grid that is contained in the Shape file
    # radius=degStep allows us to get the boundary points
    ind = path.contains_points(grid,radius=degStep)
    # Get rid of grid points outside the shapefile
    grid = grid[ind]

    # Find unique longitude (x) values
    xVal = np.unique(grid[:,1])
    
    # Find unique latitude (y) values
    yVal,yInd,yCount = np.unique(grid[:,0],return_index=True,return_counts=True)
    
    gridInfo = namedtuple('gridInfo','grid, xVal, yVal, yInd, yCount, degStep, center')
    
    return gridInfo(grid,xVal,yVal,yInd,yCount,degStep,center)

def makeShapeFile(gridData):

    w = shapefile.Writer(shapefile.POLYGON)
    w.field('id','N') # N being Integer
    w.autoBalance = 1
    count = -1
    
    # Walk through each row
    for row in range(0,len(gridData.yInd)-1):
        # For Each Row, Walk the "Cells"
        for col in range(0,gridData.yCount[row]-1):
            count += 1
            x0 = gridData.yInd[row]+col
            # We've got Lat,Lon but shapefiles want Lon,Lat (Notice Column number is 1 in xs)
            xs = gridData.grid[[x0,x0+1,x0+1,x0,x0],1]
            ys = gridData.yVal[[row,row,row+1,row+1,row]]
            # If we find a large step in X jump across the gap (comes from "Y" shape where the gap is between the Y legs)
            if (xs[1]-xs[0])>1.1*gridData.degStep:
                continue
            xypairs = [[xs[0],ys[0]],[xs[1],ys[1]],[xs[2],ys[2]],[xs[3],ys[3]],[xs[0],ys[0]]]
            w.poly(shapeType=3, parts=[xypairs])
            w.record(count)
            #shapeList.append([])

    #Save To File
    cd = os.path.dirname(os.path.realpath(__file__))
    w.save(cd+'/shapefiles/grid')
    # Convert to GeoJson
    shp2GeoJson(cd+'/shapefiles/grid.shp')
    return gridData.center

if __name__ == "__main__":
    main()
