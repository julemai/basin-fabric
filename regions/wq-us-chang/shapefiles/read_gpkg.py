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
# run read_gpkg.py


# general packages
import os
from   pathlib2  import Path

# import packages to do geoprocessing
import xarray as xr
import geopandas as gpd
from shapely.geometry import Polygon, mapping

# Shuyu's shapefiles in EPSG:5070
path = "/Users/julemai/Documents/GitHub/basin-fabric/regions/wq-us-chang/shapefiles/"
input_file = 'WQP_US_WSHD_5070_Finalized_09172024.gpkg'
    

# read data and convert to EPSG:4326
data_5070 = gpd.read_file(os.path.join(path,input_file))
data_4326 = data_5070.to_crs(4326)

# number of basins
nbasins = len(data_4326)

# basin MTWTRSHD_WQX-COMBITR01 --> has holes --> union
# basin MNPCA-S000-113         --> rings is None --> buffer introduced MULTIPOLYGONS again --> do while loop
# basin 1119USBR_WQX-CSP111    --> has still interior rings

# write shapes as SHP and JSON
for ibasin in range(nbasins):

    # basin ID is in "monitoring" (some have blanks --> make '_')
    basin_id = data_4326.loc[[ibasin]]['monitoring'].values[0].replace(' ','_')
    print('Working on basin {} ({} of {}) ...'.format(basin_id,ibasin+1,nbasins))

    # get only current basin
    aa = data_4326.loc[[ibasin]]

    while (len(aa) > 1) or (aa.iloc[0].geometry.geom_type != 'Polygon'):

        # remove MULTIPOLYGON
        aa = aa.explode(index_parts=False).reset_index().drop(columns='index')

        # derive areas
        areas = aa.to_crs(5070).area
        idx = areas.argmax()

        # derive error made by removing polygons
        area_max = areas.loc[[idx]].sum()
        area_all = areas.sum()
        pct_error = abs(1.0 - area_max/area_all)*100.
        max_error = -999.
        if pct_error > max_error:
            max_error = pct_error
        if pct_error > 0.001:
            print('WARNING :: {} :: more than 0.001% of basin area was discarded by switching to largest polygon only. Area discarded is {:.2f}%.'.format(basin_id,pct_error))

        # keep only record with largest area
        aa = aa.loc[[idx]].reset_index()

        # create buffer to resolve weird polygon issues --> this sometimes creates again a MULTIPOLYGON... so do again until there is only one POLYGON left
        aa['geometry'] = aa.buffer(0.0).make_valid()

    # fill holes
    thres_area_fill = 2000000.0 # [m2]
    rings = [ ii for ii in aa["geometry"].interiors ] # List all interior rings
    if len(rings) > 1:
        raise ValueError("Basin {} has more rings...".format(basin_id))
    else:
        rings = rings[0]
        
    for iring,ring in enumerate(rings): # if there are any rings
        ring = gpd.GeoDataFrame({'geometry': gpd.GeoSeries([ring])}, crs="EPSG:4326")
        if ring.to_crs(5070).area.loc[0] < thres_area_fill:
            #print('Ring NOT too large to remove: {} [m2]'.format(ring.to_crs(5070).area.loc[0]))
            interior_poly = [ Polygon(mapping(x)['coordinates']) for x in ring.geometry ][0]
            interior_poly = gpd.GeoDataFrame({'geometry': gpd.GeoSeries([interior_poly])}, crs="EPSG:4326").to_crs(5070).buffer(1.0).to_crs(4326)
            aa["geometry"] = aa["geometry"].union(interior_poly)

            # sometime (very rare) union leads to MULTIPOLYGON (only happened for 1119USBR_WQX-CSP111)
            if (aa.iloc[0].geometry.geom_type != 'Polygon'):
                
                # remove MULTIPOLYGON
                aa = aa.explode(index_parts=False).reset_index().drop(columns='index')

                # derive areas
                areas = aa.to_crs(5070).area
                idx = areas.argmax()

                # derive error made by removing polygons
                area_max = areas.loc[[idx]].sum()
                area_all = areas.sum()
                pct_error = abs(1.0 - area_max/area_all)*100.
                max_error = -999.
                if pct_error > max_error:
                    max_error = pct_error
                if pct_error > 0.001:
                    print('WARNING :: {} :: more than 0.001% of basin area was discarded by switching to largest polygon only. Area discarded is {:.2f}%.'.format(basin_id,pct_error))

                # keep only record with largest area
                aa = aa.loc[[idx]].reset_index()

                # create buffer to resolve weird polygon issues --> this sometimes creates again a MULTIPOLYGON... so do again until there is only one POLYGON left
                #aa['geometry'] = aa.buffer(0.0)
                
            print(">>> union of ring {} of {} gets us {} ...)) w/ {} interiors".format(iring+1,len(rings),str(aa["geometry"].iloc[0])[0:60],len([ ii for ii in aa["geometry"].interiors ][0])))
            
        else:
            print('Ring too large to remove: {} [m2]'.format(ring.to_crs(5070).area.loc[0]))

    if [ ii for ii in aa["geometry"].interiors ] != [[]]:
        print('ERROR: There is still interiors in basin {} ... HACKING'.format(basin_id))

        # this is hacking... dont know how to resolve this one polygon
        exterior_poly = gpd.GeoDataFrame({'geometry': gpd.GeoSeries([aa["geometry"].exterior[0]])}, crs="EPSG:4326")
        exterior_poly = [ Polygon(mapping(x)['coordinates']) for x in exterior_poly.geometry ][0]
        exterior_poly = gpd.GeoDataFrame({'geometry': gpd.GeoSeries([exterior_poly])}, crs="EPSG:4326").to_crs(5070).buffer(0.0).to_crs(4326)
        print('Area exterior: {:.2f} km2'.format(exterior_poly.to_crs(5070).area.iloc[0]/1000/1000))

        error = abs(1.0 - exterior_poly.to_crs(5070).area.iloc[0]/aa.to_crs(5070).area.iloc[0])*100.
        if error > 0.1:
            raise ValueError('Hacking should not be performed if area error would get too large. {} --> error = {}%'.format(basin_id,error))
        aa["geometry"] = exterior_poly

    # create buffer to resolve weird polygon issues
    aa['geometry'] = aa.buffer(0.0)

    # simplify
    aa['geometry'] = aa.to_crs(5070).simplify(0.01).to_crs(4326)

    # create folders
    foldername = os.path.join(path,basin_id)
    Path(foldername).mkdir(parents=True, exist_ok=True)

    # write as SHP
    filename = os.path.join(foldername,basin_id+'_lp.shp')
    aa.to_file(filename)

    # write as JSON
    filename = os.path.join(foldername,basin_id+'_lp.json')
    aa.to_file(filename, driver="GeoJSON")
    # aa.to_file('~/Downloads/test_aaa.json', driver="GeoJSON")

    #stop
