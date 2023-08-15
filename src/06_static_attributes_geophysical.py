#!/usr/bin/env python
from __future__ import print_function

# Copyright 2023 Juliane Mai - contact[at]juliane-mai[dot]com
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

# pyenv activate env-3.8.5-ravenpy-new
# pyenv activate env-3.8.5-basin-fabric

# python 06_static_attributes_geophysical.py -s wisconsin-lewis
# python 06_static_attributes_geophysical.py -s grip-gl-mai
# python 06_static_attributes_geophysical.py -s ontario-zhi
# python 06_static_attributes_geophysical.py -s conus-zhi
# python 06_static_attributes_geophysical.py -s north-america-mai
# python 06_static_attributes_geophysical.py -s camels-us-newman


"""

Derives static basin attributes from shapefiles (1), DEM (4), soil database (6), and landcover map (19).

    Catchment area

    Catchment mean elevation
    Standard deviation of catchment elevation
    Catchment mean slope
    Standard deviation of catchment slope

    Soil bulk density (g cm−3 )
    Soil clay content (% of weight)
    Soil gravel content (% of volume)
    Soil organic carbon (% of weight)
    Soil sand content (% of weight)
    Soil silt content (% of weight)

    Fraction of land covered by Temperate-or-sub-polar-needleleaf-forest
    Fraction of land covered by Sub-polar-taiga-needleleaf-forest
    Fraction of land covered by Tropical-or-sub-tropical-broadleaf-evergreen-forest
    Fraction of land covered by Tropical-or-sub-tropical-broadleaf-deciduous-forest
    Fraction of land covered by Temperate-or-sub-polar-broadleaf-deciduous-forest
    Fraction of land covered by Mixed-Forest
    Fraction of land covered by Tropical-or-sub-tropical-shrubland
    Fraction of land covered by Temperate-or-sub-polar-shrubland
    Fraction of land covered by Tropical-or-sub-tropical-grassland
    Fraction of land covered by Temperate-or-sub-polar-grassland
    Fraction of land covered by Sub-polar-or-polar-shrubland-lichen-moss
    Fraction of land covered by Sub-polar-or-polar-grassland-lichen-moss
    Fraction of land covered by Sub-polar-or-polar-barren-lichen-moss
    Fraction of land covered by Wetland
    Fraction of land covered by Cropland
    Fraction of land covered by Barren-Lands
    Fraction of land covered by Urban-and-Built-up
    Fraction of land covered by Water
    Fraction of land covered by Snow-and-Ice



History
-------
Written,  MG, Jan 2022
Modified, JM, Jun 2023 - modify from ipynb to python script

"""

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
from pathlib import Path

case_study   = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai', 'camels-us-newman'].")

args         = parser.parse_args()
case_study   = args.case_study

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai', 'camels-us-newman']")

del parser, args



# -----------------------
# add subolder scripts/lib to search path
# -----------------------
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+'/lib')

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import fiona
from fiona import transform
import rasterio as rio
from rasterio import mask


if case_study == 'wisconsin-lewis':
    project_root = Path(dir_path+'/../regions/wisconsin-lewis')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'ontario-zhi':
    project_root = Path(dir_path+'/../regions/ontario-zhi')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'conus-zhi':
    project_root = Path(dir_path+'/../regions/conus-zhi/')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'grip-gl-mai':
    project_root = Path(dir_path+'/../regions/grip-gl-mai/')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'north-america-mai':
    project_root = Path(dir_path+'/../regions/north-america-mai/')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

elif case_study == 'camels-us-newman':
    project_root = Path(dir_path+'/../regions/camels-us-newman/')
    types = ['shapefiles']
    filepattern = '*/*_lp.shp'

else:
    raise ValueError('Case study for {} not setup yet.'.format(case_study))

do_area      = True
do_landcover = True
do_soildata  = True
do_dem       = True


shapes = {}
shapefile_crs = None

for typ in types:
    gl_shapefiles = Path(project_root / typ ).glob(filepattern)
    cc = 0
    for gl_shp in gl_shapefiles:
        basin_id = gl_shp.parent.stem
        if basin_id in shapes:
            print(f'Already processed {basin_id}')
        with fiona.open(gl_shp) as shapefile:
            shapefile_crs = shapefile.crs
            if len(shapefile) != 1:
                raise ValueError(f'{gl_shp} contains != 1 shapes')
            shapes[basin_id] = shapefile[0]['geometry']
            cc += 1
    print(f'found {cc} {typ} basins')

if cc == 0:
    raise ValueError('No shapefile found. Used pattern {}. Check if that is correct.'.format( str(project_root) + f'/{typ}/' + filepattern))

# ---------------------------------------------------------------

if True: #do_area:

    # get area from shapefile
    area_info = pd.DataFrame(columns=['area_km2'],
                                index=shapes.keys())


    # -------------
    # grip-gl-mai (212 basins)
    # -------------
    # WISCONSIN (47 basins)
    # -------------
    # NORTH AMERICA (WEI's 513 basins)
    # -------------
    # GREAT LAKES (WEI+NANDITA 361 basins)
    # -------------
    # CAMELS-US (671 basins)
    for typ in types:
        gl_shapes = Path(project_root / typ ).glob(filepattern)
        for gl_shape in gl_shapes:
            basin = gl_shape.parent.stem
            df = gpd.read_file(gl_shape)
            df = df.to_crs('ESRI:102017')

            if len(df) != 1:
                raise ValueError(f'Found != 1 shapes in {gl_shape}')
            area_info.loc[basin, 'area_km2'] = df.loc[0, 'geometry'].area * 1e-6

    print('area_info = {}'.format(area_info))

# ---------------------------------------------------------------

if do_landcover:

    lc_classes = {
        1: 'Temperate-or-sub-polar-needleleaf-forest',
        2: 'Sub-polar-taiga-needleleaf-forest',
        3: 'Tropical-or-sub-tropical-broadleaf-evergreen-forest',
        4: 'Tropical-or-sub-tropical-broadleaf-deciduous-forest',
        5: 'Temperate-or-sub-polar-broadleaf-deciduous-forest',
        6: 'Mixed-Forest',
        7: 'Tropical-or-sub-tropical-shrubland',
        8: 'Temperate-or-sub-polar-shrubland',
        9: 'Tropical-or-sub-tropical-grassland',
        10: 'Temperate-or-sub-polar-grassland',
        11: 'Sub-polar-or-polar-shrubland-lichen-moss',
        12: 'Sub-polar-or-polar-grassland-lichen-moss',
        13: 'Sub-polar-or-polar-barren-lichen-moss',
        14: 'Wetland',
        15: 'Cropland',
        16: 'Barren-Lands',
        17: 'Urban-and-Built-up',
        18: 'Water',
        19: 'Snow-and-Ice',
    }
    lc_fractions = pd.DataFrame(columns=lc_classes.values(), index=shapes.keys())

    with rio.open(project_root / '../..' / 'data' / 'landcover' / 'NA_NALCMS_2010_v2_land_cover_30m.tif') as gridded_ds:
        for basin, shape in shapes.items():

            # transform shape to gridded_ds crs
            transformed_shape = transform.transform_geom(shapefile_crs, gridded_ds.crs.data, shape)

            # crop to basin outline
            cropped_ds, _ = mask.mask(gridded_ds, [transformed_shape], crop=True,
                                      filled=True, nodata=gridded_ds.nodata)
            cropped_ds = cropped_ds.astype( float )
            cropped_ds[cropped_ds == gridded_ds.nodata] = np.nan

            for lc_id, lc_class in lc_classes.items():
                lc_fractions.loc[basin, lc_class] = (cropped_ds == lc_id).sum() / (~np.isnan(cropped_ds)).sum()

    print('lc_fractions = {}'.format(lc_fractions))

# ---------------------------------------------------------------

if do_soildata:

    soil_sets = ['BD', 'CLAY', 'GRAV', 'OC', 'SAND', 'SILT']
    soil_data = pd.DataFrame(columns=soil_sets, index=shapes.keys())

    for basin, shape in shapes.items():
        # transform shape to gridded_ds crs
        transformed_shape = transform.transform_geom(shapefile_crs, {'init': 'epsg:4326'}, shape)

        for soil_set in soil_sets:

            # soil data is split in two nc files, one containing the first 4 soil layers the other the second 4.
            cropped = []
            for i in [1, 2]:
                with rio.open(project_root / '../..' / 'data' / 'soil' / f'{soil_set}{i}.nc') as gridded_ds:
                        # crop to basin outline
                        cropped_ds, _ = mask.mask(gridded_ds, [transformed_shape], crop=True,
                                                  filled=True, nodata=gridded_ds.nodata)
                        cropped_ds = cropped_ds.astype( float )
                        cropped_ds[cropped_ds == gridded_ds.nodata] = np.nan
                        cropped.append(cropped_ds)

            cropped = np.concatenate(cropped, axis=0)
            soil_data.loc[basin, soil_set] = np.nanmean(cropped_ds)

    print('soil_data = {}'.format(soil_data))

# ---------------------------------------------------------------

if do_dem:

    dem_info = pd.DataFrame(columns=['mean_elev', 'mean_slope', 'std_elev', 'std_slope'],
                            index=shapes.keys())

    with rio.open(project_root / '../..' / 'data' / 'dem' / 'na_ca_dem_3s.tif') as gridded_ds:
        for basin, shape in shapes.items():

            # transform shape to gridded_ds crs
            transformed_shape = transform.transform_geom(shapefile_crs, gridded_ds.crs.data, shape)

            # crop to basin outline
            cropped_ds, _ = mask.mask(gridded_ds, [transformed_shape], crop=True,
                                      filled=True, nodata=gridded_ds.nodata)
            cropped_ds = cropped_ds.astype( float )
            cropped_ds[cropped_ds == gridded_ds.nodata] = np.nan

            dem_info.loc[basin, 'mean_elev'] = np.nanmean(cropped_ds)
            dem_info.loc[basin, 'std_elev'] = np.nanstd(cropped_ds)

    # leave slope calculation to GDAL. Horizontal units are degrees, vertical units are meters,
    # hence the scale factor (see https://gdal.org/programs/gdaldem.html)
    # !/system/apps/userenv/gauch/nh/bin/gdaldem slope -s 111120 gridded/dem/na_ca_dem_3s.tif /tmp/tmp-slope.tif
    # --> DONE: see gridded/dem/README.md

    with rio.open(project_root / '../..' / 'data' / 'dem' / 'na_ca_dem_3s-slope.tif', driver='GTiff') as gridded_ds:
        for basin, shape in shapes.items():

            # transform shape to gridded_ds crs
            transformed_shape = transform.transform_geom(shapefile_crs, gridded_ds.crs.data, shape)

            # crop to basin outline
            cropped_ds, _ = mask.mask(gridded_ds, [transformed_shape], crop=True,
                                      filled=True, nodata=gridded_ds.nodata)
            cropped_ds = cropped_ds.astype( float )
            cropped_ds[cropped_ds == gridded_ds.nodata] = np.nan

            dem_info.loc[basin, 'mean_slope'] = np.nanmean(cropped_ds)
            dem_info.loc[basin, 'std_slope'] = np.nanstd(cropped_ds)

    print('dem_info = {}'.format(dem_info))

# ---------------------------------------------------------------


# merge information collected

static_attrs = area_info

if do_landcover:
    static_attrs = static_attrs.join(lc_fractions)
if do_soildata:
    static_attrs = static_attrs.join(soil_data)
if do_dem:
    static_attrs = static_attrs.join(dem_info)

# Make sure output directory exists
os.makedirs( Path(project_root / 'attributes'), exist_ok=True )

static_attrs.index.set_names('basin', inplace=True)
filename_out = Path(project_root / 'attributes' / 'static_attributes.csv')
static_attrs.to_csv(filename_out)

print('Saved information to: {}'.format(filename_out))
