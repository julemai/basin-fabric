#!/usr/bin/env python
from __future__ import print_function

# Copyright 2025 Juliane Mai - contact[at]juliane-mai[dot]com
#
# License
# This file is part of Juliane Mai's personal code library.
#
# Juliane Mai's personal code library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Juliane Mai's personal code library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with Juliane Mai's personal code library.  If not, see <http://www.gnu.org/licenses/>.
#



# pyenv activate env-3.11.9
# run get_data.py


# remove basins smaller than 300 km2?
do_remove_small_basins = True 


# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/../../../src/additional_processing')


# general packages
import os
import glob as glob
import json
from   pathlib2  import Path
import datetime as datetime
import numpy as np
import pandas as pd
import shutil

# import packages to do geoprocessing
import geopandas as gpd

# import converter to shapefile
from coords2shapefile import coords2shapefile

def in_range(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime.datetime(1980, 1, 1) <= d <= datetime.datetime(2018, 12, 31)

# folder that has delineated basin shapefiles
inpath = "/Users/julemai/Desktop/datastream_station_analysis/delineated/20250922/all-nutrients/"

# folder to save basin shapefiles in
outpath = "/Users/julemai/Documents/GitHub/basin-fabric/regions/wq-ca-mai/shapefiles/"

# files containing filtered+merged observation
obspath = "/Users/julemai/Documents/GitHub/datastream/data/step_3_merged_data/20251014/"
files_obs = [
    obspath+'daily_concentration_nitrate_min-years-0.json',
    obspath+'daily_concentration_orthophosphate_min-years-0.json',
    obspath+'daily_concentration_total-nitrogen_min-years-0.json',
    obspath+'daily_concentration_total-phosphorus_min-years-0.json'
    ]

# files containing pairs of Q-C stations
pairspath = "/Users/julemai/Desktop/datastream_station_analysis/pairs_v1_v2_v3_20251016/"
files_pairs = [
    pairspath+"pairs_v3_nitrate.csv",
    pairspath+"pairs_v3_orthophosphate.csv",
    pairspath+"pairs_v3_total-nitrogen.csv",
    pairspath+"pairs_v3_total-phosphorus.csv"
    ]



# -----------------------------------------------------------------------------------------------
# start code
# -----------------------------------------------------------------------------------------------

# read all observations
obs_data_all = {}
for file_obs in files_obs:

    tmp_data = {}
    
    with open(file_obs, "r") as ff:
        data = json.load(ff)

        for station in list(data.keys()):

            dates = list(data[station]['data_obs'].keys())
            dates_1980_2018 = [ dd for dd in dates if in_range(dd) ]
            if len(dates_1980_2018) > 0:
                # keep data if there are observations for this station
                tmp_data[station] = data[station]

    obs_data_all[file_obs] = tmp_data

# get stations where at least one solute has observations
stations_with_data = []
for file_obs in files_obs:
    stations_with_data += list(obs_data_all[file_obs].keys())
stations_with_data = np.sort(np.unique(stations_with_data))
#print('Number of stations found that have data between 1980 and 2018 for at least one solute: {}'.format(len(stations_with_data)))

# read all pairs
pairs_data_all = {}
for file_pairs in files_pairs:

    df = pd.read_csv(file_pairs,
                         dtype={
                             "station_q": "string",
                             "station_c": "string",
                             "name_q": "string"
                             })

    for row in df.itertuples():
        pairs_data_all[row.station_c] = {
            "station_q": row.station_q,
            "name_q": row.name_q
        }


# get all files with delineated basins
files_delineated = glob.glob(inpath+'*.geojson')   # '<basin_id>.geojson'

nstations_obs        = 0
nstations_loc_ok     = 0
nstations_area_10000 = 0
if do_remove_small_basins:
    nstations_area_300   = 0
nstations_colocated  = 0
# count observations: {'nitrate': 0, 'orthophosphate': 0, 'total nitrogen': 0, 'total phosphorus': 0}
nutrient_types = [ obs_data_all[file_obs][list(obs_data_all[file_obs].keys())[0]]['nutrient_type'] for file_obs in files_obs ]
nobs_selected_stations = { nutrient_types[ifile_obs]: 0 for ifile_obs,file_obs in enumerate(files_obs) }

if do_remove_small_basins:
    filename = os.path.join( Path(outpath).parent, "basins_wo_small_basins.csv")
else:
    filename = os.path.join( Path(outpath).parent, "basins_w_small_basins.csv")
    
with open(filename, "w") as ff:
    ff.write("id,name,lat,lon,obs_q\n")

    for file_delineated in np.sort(files_delineated):

        # basin ID
        basin_id = Path(file_delineated).stem

        # get if station has data for at least one solute between 1980-01-01 and 2018-12-31
        if basin_id in stations_with_data:
            has_obs = True
            nstations_obs += 1
        else:
            continue

        # read delineated shapefile (for area)
        gdf = gpd.read_file(file_delineated)

        # make sure basin is not entirly above 60N (DEM not available there)
        bbox = gdf.total_bounds  # returns (minx, miny, maxx, maxy)
        if bbox[1] > 60.0:
            #print('DEM elevation: Skip basin {} since it is entirely above 60N and DEM not available there. bbox = (minx, miny, maxx, maxy) = {}'.format(basin_id,bbox))
            continue
        else:
            nstations_loc_ok += 1

        # determine area  (needs to be between 300km2 and 10,000km2)
        if 'area_calc_sqkm' in gdf.iloc[0].keys(): # Kasope
            area = gdf.iloc[0]['area_calc_sqkm']
        else:
            raise ValueError('Area not found for basin {}.'.format(basin_id))

        if area < 10000.0:
            nstations_area_10000 += 1
        else:
            continue

        if do_remove_small_basins:
            if area > 300.0:
                nstations_area_300 += 1
            else:
                continue

        # get lat/lon (just for basin.csv)
        if 'lng' in gdf.iloc[0].keys(): # Kasope
            lon = gdf.iloc[0]['lng']
        else:
            raise ValueError('Longitude not found for basin {}.'.format(basin_id))
        
        if 'lat' in gdf.iloc[0].keys(): # Kasope
            lat = gdf.iloc[0]['lat']
        else:
            raise ValueError('Latitude not found for basin {}.'.format(basin_id))

        # count number of C observations
        for ifile_obs,file_obs in enumerate(files_obs):
            if basin_id in obs_data_all[file_obs].keys():
                nn = len(obs_data_all[file_obs][basin_id]['data_obs'])
                nobs_selected_stations[nutrient_types[ifile_obs]] += nn

        # get co-located Q station (not needed but nice to have)
        if basin_id in pairs_data_all.keys():
            name = pairs_data_all[basin_id]["name_q"]
            obs_q = pairs_data_all[basin_id]["station_q"]
            nstations_colocated += 1
        else:
            name = "unknown"
            obs_q = ""

        # add to basin.csv
        ff.write("{},{},{},{},{}\n".format(basin_id,name,lat,lon,obs_q))  # ff.write("id,name,lat,lon,obs_q \n")

        # write shapefile
        filename_shp = basin_id+"_lp"
        if len(gdf) > 1:
            raise ValueError('Multiple features found')
        else:
            geom = gdf.loc[0, "geometry"]

            # If it's a Polygon --> just use it
            if geom.geom_type == "Polygon":
                poly = geom

            # If it's a MultiPolygon --> select the largest polygon by area
            elif geom.geom_type == "MultiPolygon":
                poly = max(geom.geoms, key=lambda p: p.area)
    
            coords = list(poly.exterior.coords)
        coords2shapefile(filename_shp,coords)

        # write as GeoJSON
        filename_json = filename_shp+".json"
        shape_subbasins = gpd.read_file(filename_shp+'.shp')  # is a GeoPandas DataFrame
        json_dict = json.loads(gpd.GeoDataFrame(shape_subbasins, crs="EPSG:4326").to_json())  # is a dictionary
        with open(filename_json, "w") as outfile:
            json.dump(json_dict, outfile)

        # move JSON file to outpath
        src = Path(filename_json)
        dst = Path(basin_id+'/'+filename_json)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

        # remove SHP files
        shp_files = glob.glob(filename_shp+'.*')
        for shp_file in shp_files:
            #print(shp_file)
            os.remove(shp_file)
        

print('Total number of successfully delineated stations:           {:>5d}'.format(len(files_delineated)))
print('Number of stations with data between 1980 and 2018:         {:>5d} of {:>5d}'.format(nstations_obs,len(files_delineated)))
print('Number of stations located not entirely above 60N (no DEM): {:>5d} of {:>5d}'.format(nstations_loc_ok,nstations_obs))
print('Number of station smaller than 10000 km2:                   {:>5d} of {:>5d}'.format(nstations_area_10000,nstations_obs))
if do_remove_small_basins:
    print('Number of station larger  than   300 km2:                   {:>5d} of {:>5d}'.format(nstations_area_300,nstations_area_10000))
    print('Number of station colocated with obs_q stations:            {:>5d} of {:>5d}'.format(nstations_colocated,nstations_area_300))
    print("")
    print('Total number of C observations across the {} stations selected:'.format(nstations_area_300))
else:
    print('Number of station colocated with obs_q stations:            {:>5d} of {:>5d}'.format(nstations_colocated,nstations_area_10000))
    print("")
    print('Total number of C observations across the {} stations selected:'.format(nstations_area_10000))

for ii in nobs_selected_stations:
    print("    {:>20s}: {:>7d}".format(ii,nobs_selected_stations[ii]))
