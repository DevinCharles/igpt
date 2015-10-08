# igpt - Interactive Geospatial Plotting Toolkit
##Intro
The goal of the igpt (*pronounced Egypt*) package is to provide a group of tools that extends some matplotlib type plotting to the geospatial realm in an easy to use format. Ideally this would become a plugin for folium, or at least include one to allow more ability on the actual representation of the plots on the map. Full disclosure, I am not a python programmer, or an anything programmer really. I'm learning as I go, and this my first real project. Expect mistakes and a malestrom of hacked together commits in an attempt to perpetually fix what was almost once working.

##shapefileGrid & blockIndexer
So far only the shapefileGrid and blockIndexer tools exist. The first will break any shapefile drawn by latitude and longitude (json or shp) into a grid of specified size. From there, blockIndexer will check a data file you give it and determine where each of the lines of data file are in relation to the grid. It's option Frequency=True takes the output of blockIndexer and determines how many times things occur in each of the blocks of the grid. 

While block indexer was written for the shapefileGrid output, but it has the ability to read any group of shapefiles and index any lat, lon containing data set, however it currently only uses the bounding boxes of the shapes, which helps give it it's speed (*in the example it checks 52k events agains ~9000 shapefiles in a few seconds, that's 468 million combinations*). In the near future it will have a switch for non-grid shapefiles that will use mpl.path which should give better results for irregular shapes. The next step to speed up even larger data sets will be to use self organizing maps, but that's some time out still.

##isoShapes
This is the next planed tool for the toolkit, creating isoplot like shapefiles indexed with block indexer to show where things happen. Shapes could be filled or given colored lines (maybe?) to show as isolines.

##findShapeFiles
This will be a tool to help find shapefiles using natural language lookups. Maybe.

##findDataSets
Same idea for datasets. Same maybe.

##Examples
#### Shapefile Grids
`from igpt import grids_example`
`# "Create a Low Density" grid`
`grids_example('low')`
