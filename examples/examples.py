from igpt import shapefileGrid,blockIndexer,mapGenerator

def grids_example():
    # Open the Outline of Philadelphia Shapefile, Create grid with Defaults, Make the New Shapefile
    shpfile = r'examples/ex_grids/shapefiles/Philadelphia_City_Limits.json'
    gridData = shapefileGrid(shpfile,return_data=True)

    center = gridData.center

    # Run blockIndexer against the Philadelphia Crime incidents file
    # This is sort through the 52k lines of incidents and determine
    # in which block of the grid they belong
    datafile = r'examples/ex_grids/datafiles/police_inct.csv'

    # These are the Columns in the Data file with Lat and Lon Coords
    latcol = 'POINT_Y'
    loncol = 'POINT_X'
    shpfile = r'grids/shapefiles/grid.shp'
    # This is the polygon identifier. It will look for the record of the
    # field 'id' and use that to index the data. These record (value) can be
    # a string or a number.
    ID = 'id'

    # Adding Frequency=True generates the histogram data (number of events per block)
    datafile,data_columns,data_size = blockIndexer(datafile,latcol,loncol,shpfile,ID,frequency=True)

    # Create the Map and Serve the Files
    color = 'YlOrBr'
    legend = 'Number of Crime Occurances YTD Oct 2015'

    files = shpfile,datafile
    data_info = data_columns,'feature.properties.'+ID,center
    map_opts = color,legend

    print('Grid Size:\t',gridData.grid.shape[0])    
    print('Data Size:\t',data_size)

    try:
        mapGenerator(files,data_info,map_opts,serve_files=True)
    except (KeyboardInterrupt, SystemExit):
        raise

#if __name__ == "__main__":
#    main()
