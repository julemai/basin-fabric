# Workflow for WRTDS-K basins displayed on POSEIDON


## Basin IDs and some information

Original GeoJSON shapefile:
/Users/julemai/Documents/GitHub/nutrihub-webpage/data/dataset-03_WRTDS_20251016/dataset-03_download_Point_geometry.js

Other information, like outlet lat/lon:
/Users/julemai/Documents/GitHub/nutrihub-webpage/data/dataset-03_WRTDS_20251016/dataset-03_download_Point_geometry.js

Create shapefile for GeoJSON features by adding this to end of
`coords2shapefile.py` which will create all shapefiles and the `basins.csv`:
```
    path_to_file_shp    = '../../regions/wrtdsk-mai/dataset-03_download_Point_geometry.js'
    path_to_file_latlon = '../../regions/wrtdsk-mai/dataset-03_download_Point.js'

    import geojson
    import geopandas as gpd
    import json
    import numpy as np
    import math
    import pandas as pd

    def handle_nan(val):
        if val == "NaN":
            return math.nan
        raise ValueError(f"Unexpected constant: {val}")

    with open(path_to_file_shp) as ff1:
        gj = geojson.load(ff1)

    with open(path_to_file_latlon) as ff2:
        gjll = geojson.load(ff2, parse_constant=handle_nan)
    # array of ids for lookup
    llids = np.array([ gjll['features'][ii]['properties']['id'] for ii in range(len(gjll['features'])) ])
        
    nfeatures = len(gj['features'])

    count_wo_shp_file = 0
    count_w_shp_file = 0
    dict_meta = {}
    for ifeature in range(nfeatures):

        basin = gj['features'][ifeature]['properties']['id']
        filename = '../../regions/wrtdsk-mai/shapefiles/{}/{}_lp'.format(basin,basin)

        if gj['features'][ifeature]['properties']['area_km2_5070'] > 0.0:

            print('Working on basin {} ({} of {})'.format(basin,ifeature+1,nfeatures))

            # write shapefile
            coords = gj['features'][ifeature]['geometry']['coordinates'][0]
            coords2shapefile(filename,coords)

            # write as GeoJSON
            shape_subbasins = gpd.read_file(filename+'.shp')  # is a GeoPandas DataFrame
            json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
            with open(filename+".json", "w") as outfile:
                json.dump(json_dict, outfile)

            count_w_shp_file += 1

            idx = np.where(np.array(llids)==basin)[0]
            if len(idx) > 0:
                idx = idx[0]
                dict_meta[basin] = {  "id":    gjll['features'][idx]['properties']["id"],
                                      "name":  gjll['features'][idx]['properties']["name"].replace(',',';'),
                                      "lat":   gjll['features'][idx]['properties']["lat_deg_c"],
                                      "lon":   gjll['features'][idx]['properties']["lon_deg_c"],
                                      "obs_q": gjll['features'][idx]['properties']["station_q"]
                                    }

        else:

            print('Working on basin {} ({} of {}) --> discarded because shapefile not known'.format(basin,ifeature+1,nfeatures))

            count_wo_shp_file += 1

    if len(dict_meta) != count_w_shp_file:
        raise ValueError('Number of basins we wrote shapefiles for does not match number of basins with metadata available.')

    # convert to DataFrame
    df = pd.DataFrame.from_dict(dict_meta, orient='index')

    # reorder columns
    df = df[['id', 'name', 'lat', 'lon', 'obs_q']]

    # save to CSV
    filename = "../../regions/wrtdsk-mai/basins.csv"
    df.to_csv(filename, index=False)

    print("Number of basins where we did not know shapefile (all US since Kim did not provide shapefiles: {}".format(count_wo_shp_file))
    print("Number of basins with shapefile and other info available:                                      {}".format(count_w_shp_file))

    print('')
    print('Wrote: {}'.format(filename))

```



## Plot map showing basins

Plot all the shapes on a map. Basically to check if this all makes
sense and shapefiles are readible.
```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-nrcan
cd basin-fabric/src
python 04_plot_basin_map.py -s wrtdsk-mai
```

Creates: maps/map.png


## Derive geophysical attributes

Derive static attributes from geophysical datasets, i.e. DEM, soil,
and landcover, and save them in a CSV file.

The wetlands are so tiny that some require `all_touched=True` for the
SOIL data.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-ravenpy-new
python src/06_static_attributes_geophysical.py -s wrtdsk-mai
```

Creates: attributes/static_attributes.csv


## Clip nutrients

Extract nutrients for each basin wrtds-k from gTREND-P-Canada_v1.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric

basins=$( \ls -d ../regions/wrtdsk-mai/shapefiles/[0-9]* | rev | cut -d '/' -f 1 | rev )
for bb in $basins ; do echo '' ; echo '-------------------' ; echo $bb ; python 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b ${bb} -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac ; done
```

Creates: forcings/*/*_agg_gTREND-P-CA_v1.csv


## Clip forcings

Extract forcings for each basin wrtdsk-mai from RDRS-v2.1.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/07_create_lumped_forcings.py -s wrtdsk-mai -b XXXX -f /scratch/julemai/basin-fabric/data/meteorology/rdrs-v2.1_north-america/ -y graham
```

Creates: forcings/*_agg_*_*_lp.nc


## Derive meteorologic attributes

Derive attributes based on meteorology.

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/08_static_attributes_forcings.py -s wrtdsk-mai -f 'rdrs-v2.1_north-america' -p 'all' -a 
```

Creates: attributes/climate_indices.csv
Creates: forcings/*_agg_*_*_lp_daily_local.nc

Add produced files to Git:
```
git add regions/wrtdsk-mai/forcings/*/*_agg_*_daily_local.nc
```


## Check and plot attribute values

```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/17_plot_attributes.py -s 'wrtdsk-mai' -f 'rdrs-v2.1_north-america'
```

Creates: ../regions/wrtdsk-mai/attributes/climate_indices_rdrs-v2.1_north-america.pdf


## Check forcings

Checks the forcing files and ranges of variables:
```
source /project/6070465/julemai/basin-fabric/env-3.11/bin/activate 
pyenv activate env-3.8.5-basin-fabric
python src/18_check_all_forcing_files.py -s 'wrtdsk-mai' -f 'rdrs-v2.1_north-america' 
```



