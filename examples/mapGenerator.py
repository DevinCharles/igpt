# coding: utf-8

import folium
import pandas as pd
from os.path import splitext

def mapGenerator(files,data_info='default', map_opts='default',serve_files=False):

    createMap(files,data_info, map_opts)

    if serve_files:
            try:
                startServer()
            except Exception as e:
                print(str(e))

def getDefaults(empty_input):
    if empty_input is 'map_opts':
        return 'YlOrBr','Data'
    elif empty_input is 'data_info':
        return ['GRID_ID','FREQ'],'feature.properties.id',[40.0, -75.14]

def startServer(address = "127.0.0.1",port = 8765):
    try:
        # Python 2.x
        from SimpleHTTPServer import SimpleHTTPRequestHandler
        import SocketServer as socketserver
    except:
        # Python 3.X
        from http.server import SimpleHTTPRequestHandler
        import socketserver
    
    Handler = SimpleHTTPRequestHandler

    httpd = socketserver.TCPServer((address, port), Handler)

    print('Serving on http://127.0.0.1:8765')
    httpd.serve_forever()

def createMap(files,data_info='default', map_opts='default'):
    # Input Handling
    try:
        geo_file,data_file = files
    except ValueError:
        print('You need to give shapefile name and a CSV data file name.')
        return
    try:
        color,legend = map_opts
    except ValueError:
        color,legend = getDefaults('map_opts')
    try:
        columns,shape_id,center = data_info
    except ValueError:
        color,legend = getDefaults('data_info')
        
    # If Shapefile is .shp, convert it
    root,ext = splitext(geo_file)
    if ext == '.shp':
        from igpt import shp2GeoJson
        shp2GeoJson(geo_file)
        geo_file = root+'.json'
        
    # Make Sure Name is .html
    #root,ext = splitext(name)
    #name = root+'.html'
    
    # Check if Data file is dataframe or csv
    if type(data_file) is pd.core.frame.DataFrame:
        data = data_file
    elif data_file[-3:] =='csv':
        data = pd.read_csv(data_file)
    else:
        print('data_file must be a Pandas Data Frame or the path to a csv file')
        return
    # Build Shape ID
    id_parts = shape_id.split('.')

    if len(id_parts) == 1:
        full_id = 'feature.'+id_parts[0]
    else:
        full_id = shape_id
    
    # Create Simple Folium Map
    map = folium.Map(location=center, zoom_start=11)
#   try:
    map.geo_json(geo_path=geo_file, data=data,
                 columns=columns,
                 key_on=full_id,
                 fill_color=color, fill_opacity=0.7, line_opacity=0.2,
                 legend_name=legend,
                 reset=True)

#    except Exception as e:
#        print(e)
#        print('You tried ID: ',full_id)
#        full_id = 'feature.properties.'+id_parts[-1]
#        print('Trying again with ID: ',full_id)
#        try:
#            map.geo_json(geo_path=geo_file, data=data,
#                     columns=columns,
#                     key_on=full_id,
#                     fill_color=color, fill_opacity=0.7, line_opacity=0.2,
#                     legend_name=legend,
#                     reset=True)
#            print('Sucess with new ID')
#        except Exception as e:
#            print('Failed again...')
#            return      

    map.create_map(path='index.html')

if __name__ == "__main__":
    main()

