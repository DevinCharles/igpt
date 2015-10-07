# coding: utf-8
import numpy as np
import pandas as pd
import shapefile
import os
#from pyproj import Proj

def blockIndexer(datafile,latcol,loncol,shpfile,ID,frequency=False):
    filename,column,data_size = numberCruncher(datafile,latcol,loncol,shpfile,ID)
    columns = (column,'')
    if frequency:
        filename,columns = freqFileGen(filename,column)
    return filename,columns,data_size       

# This is a nightmare, and doesn't work... but is it the lesser of two evils over compiling gdal for python?
# Attempt to change projection
#def changeProj(x,y,filename):
#    epsg42304=pyproj.Proj("+proj=lcc +lat_1=49 +lat_0=49 +lon_0=-95 +k_0=1 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=ft +no_defs")
#    with open(filename+'.prj') as f:
#        prj_data = f.read()
#        projection = prj_data.split('PROJECTION["')[1].split('"]')[0]
#    if projection == 'Lambert_Conformal_Conic':
#        x,y = epsg42304(x,y,inverse=True)
#    return x,y

# Generator to loop through datafile rows and shapes in shapefile to determine if each 
# event in the data file lies within each shape in the shape file. 
def makeGen(coords,bboxes):
    # For Every Lon,Lat Coordinate
    for c_ind, coord in enumerate(coords):
        x,y = coord
        # For Every Polygon(bbox) in Shapefile
        for b_ind, bbox in enumerate(bboxes):
            (x0,x1),(y0,y1) = bbox
            if(x0<x<x1 and y0<y<y1):
                #print('x0:',x0,'x:',x,'x1:',x1)
                #print('y0:',y0,'y:',y,'y1:',y1)
                yield (c_ind,b_ind)
                break

def dfUpdater(indexes,id_list):
    row = indexes[0]
    shape_id = id_list[indexes[1]]
    return [row,shape_id]

def numberCruncher(datafile,latcol,loncol,shpfile,ID):
    # File Roots and Extensions
    root,ext = os.path.splitext(datafile)
    sfroot,sfext = os.path.splitext(shpfile)
    # Read the Lon, Lat Coords into a DataFrame
    df = pd.read_csv(datafile)
    # Get number of rows and columns, and lon(x) and lat(y)
    nr,nc = df.shape
    x = np.array(df[loncol])
    y = np.array(df[latcol])

    # Read the Shapefile
    # TODO: Fiona Implementation for GeoJson Shapefiles
    # maybe remove pyshp completely and convert all shp to json?
    sf = shapefile.Reader(shpfile)
    shapes = sf.shapes()
    fields = sf.fields
    records = sf.records()

    # Find the Field in the Shapefile Containing the ID
    # this is how we identify our polygons 
    for ind in range(1,len(fields)):
        if (ID in fields[ind]):
            # ind-1 because of (DELETEFLAG) field
            rec_ind = ind-1
            break
    try:
        rec_ind
    except:
        print("Couldn't find ID in Shapefile Fields\n See fields below.\n")
        print(fields)
        return
        #sys.exit("Couldn't find ID in Shapefile Fields\n See fields in terminal.")
            

    id_list = []
    bboxes = []
    
    #TODO: BBOX ONLY WORKS FOR GRID SHAPES, WON'T WORK FOR IRREGULAR SHAPES
    # NEED TO USE mpl.path.contains_points WHICH WILL BE SLOWER
    # SWITCH ON TYPE?
    
    # Get IDs and bounding boxes of all shapes
    for ind in range(0,len(shapes)):
        id_list.append(records[ind][rec_ind])
        x0,y0,x1,y1 = shapes[ind].bbox
        #if(abs(x0)>180):
            #[x0,x1],[y0,y1] = changeProj([x0,x1],[y0,y1],sfroot)
        bboxes.append(((x0,x1),(y0,y1)))
    
    # Reshape coords as a list of tuples (x,y)
    coords_list = np.append(np.vstack(x),np.vstack(y),axis=1).tolist()
    coords = [tuple(l) for l in coords_list]
    
    # Create Generator and loop through
    data = []
    generator = makeGen(coords,bboxes)
    
    for each in generator:
        data.append(dfUpdater(each,id_list))
    
    # Create Column of the Shapes at the correct row indicies
    data = np.array(data)
    ind = np.array(data[:,0]).astype(int)
    val = np.array(data[:,1])
    col = np.empty(df.shape[0])*np.nan
    if val.dtype.kind==np.array(['A']).dtype.kind:
        col = col.astype(val.dtype)
    col.flat[ind]=val
    col = col.tolist()
    
    filename = root+'_Grid.csv'
    column = 'GRID_ID'   

    # Add the Shape Column to the Data Frame
    values = np.insert(df.values,df.shape[1],col,axis=1)
    header = df.columns.values.tolist()
    header.append(column)
    df = pd.DataFrame(values,columns=header)
    df.to_csv(filename, sep=',', encoding='utf-8')

    return filename,column,df.shape[0]

def freqFileGen(datafile,column):
    root,ext = os.path.splitext(datafile)
    df = pd.read_csv(datafile, low_memory=False)
    x,y = np.unique(df[column],return_counts = True)
    x =  x.astype(int)
    df = pd.DataFrame({'GRID_ID':x[:],'FREQ':y[:]})
    filename = root+'_hist.csv'
    df.to_csv(filename, sep=',', encoding='utf-8')
    return filename,('GRID_ID','FREQ')

if __name__ == "__main__":
    main()
