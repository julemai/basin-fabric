#!/usr/bin/env python
## License

# Copyright 2024 Juliane Mai - juliane.mai@uwaterloo.ca
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


# pyenv activate env-3.11.9

# (a) basin with no coverage --> NO OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 645722 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac

# (b) basin has technically coverage (bbox) but no actual data available (all values are nan) --> NO OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 01549700 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac

# (c) basin between alberta and BC -- everything is 0.0 --> OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 221096 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac

# (d) basin in Ontario -- everything has a value --> OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 417229 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac

# (e) basin that is very small (~3km2) --> OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 220369 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac

# (f) basin that has 3 times output --> OUTUT WRITTEN
# run 07_create_lumped_forcings_gTREND-P-CA_v1_all_provinces.py  -s wrtdsk-mai -b 6645 -f ../data/nutrients/gTREND-P-CA_v1/gTREND-P-Canada_v1_*.nc -y mac


from __future__ import print_function

# -------------------------------------------------------------------------
# Command line arguments
#

import argparse
import sys
import os

import xarray as xr
import rioxarray
import geopandas as gpd
import pandas as pd
import numpy as np
import glob
from pathlib2 import Path
import rasterio.errors

case_study   = None
forcings     = glob.glob( os.path.join('..','..','data','nutrients','gTREND-P-CA_v1','gTREND-P-Canada_v1_*.nc') )
basin        = None
system       = None

parser  = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                  description='''Derive static geophysical attributes.''')
parser.add_argument('-s', '--case_study', action='store', default=case_study, dest='case_study',
                    help="Case study. One of ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai'].")
parser.add_argument('-f', '--forcings', action='store', default=forcings, dest='forcings',nargs='+',
                    help="Name of folder containing nutrients for a larger region (e.g., Great Lakes or North America).")
parser.add_argument('-b', '--basin', action='store', default=basin, dest='basin',
                    help="Name of basin to process. Shapefile in subfolder 'shapefile' is assumed to be named like this ID.")
parser.add_argument('-y', '--system', action='store', default=system, dest='system',
                    help="Name of system. Either 'graham' or 'mac'.")

args         = parser.parse_args()
case_study   = args.case_study
forcings     = args.forcings
basin        = args.basin
system       = args.system

if (case_study is None):
    raise ValueError("Case study (-s) must be specified and need to be one of the following: ['wisconsin-lewis', 'ontario-zhi', 'conus-zhi', 'grip-gl-mai']")

if (forcings is None):
    raise ValueError("Name of folder containing gridded forcings for larger domain (-f) must be specified.")


del parser, args


from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')



out_filename = Path(str(Path(__file__).parent)+'/../regions/wrtdsk-mai/forcings/{}/{}_agg_gTREND-P-CA_v1.csv'.format(basin,basin))

if False: #os.path.exists(out_filename):  # 

    print('File {} already exists. Will be skipped.'.format(out_filename))

else:

    # -----------------------------
    # User inputs
    # -----------------------------
    netcdf_files = np.sort(forcings)
    watershed_shp = Path(str(Path(__file__).parent)+'/../regions/wrtdsk-mai/shapefiles/{}/{}_lp.shp'.format(basin,basin))

    # Load watershed shapefile
    watershed = gpd.read_file(watershed_shp)

    # Dictionary to store per-variable aggregated data
    agg_sum = {}
    agg_area = {}

    # -----------------------------
    # Loop over NetCDF files
    # -----------------------------
    for ff in netcdf_files:
        print(f"Processing {ff}...")
        
        # Open dataset lazily with dask for memory efficiency
        ds = xr.open_dataset(ff) #, chunks={"x": 1000, "y": 1000})
        
        # Set CRS from grid_mapping
        if not ds.rio.crs:
            ds = ds.rio.write_crs(ds.albers_conical_equal_area.crs_wkt)
        
        # Reproject watershed to NetCDF CRS
        watershed_proj = watershed.to_crs(ds.rio.crs)

        # Dataset bounds
        ds_bounds = ds.rio.bounds()  # xmin, ymin, xmax, ymax
        ws_bounds = watershed_proj.total_bounds  # xmin, ymin, xmax, ymax

        # Check for intersection
        if (ds_bounds[2] < ws_bounds[0] or
            ds_bounds[0] > ws_bounds[2] or
            ds_bounds[3] < ws_bounds[1] or
            ds_bounds[1] > ws_bounds[3]):
            print(f"  Skipping {ff}: no intersection with watershed.")
            continue


        # Clip all variables first
        clipped_vars = {}
        for var in ds.data_vars:
            try:
                clipped = ds[var].rio.clip(
                    watershed_proj.geometry,
                    watershed_proj.crs,
                    drop=True,
                    all_touched=False
                )
                # Mask unrealistic or placeholder values (common threshold)
                clipped = clipped.where((clipped >= -1e30) & (clipped <= 1e30))
                clipped_vars[var] = clipped
            except Exception as e:
                print(f"  Skipping {var}: {e}")
                continue

        # Build a combined validity mask across all clipped variables
        # (True where *any* variable is valid)
        combined_valid_mask = None
        for clipped in clipped_vars.values():
            mask = ~clipped.isnull()
            combined_valid_mask = mask if combined_valid_mask is None else (combined_valid_mask & mask)

        # Apply combined mask to all clipped variables
        for var in clipped_vars:
            clipped_vars[var] = clipped_vars[var].where(combined_valid_mask)

        # Compute per-grid-cell area (same for all vars)
        example_var = next(iter(clipped_vars.values()))
        cell_area = xr.ones_like(example_var.isel(time=0)) * abs(
            ds.rio.resolution()[0] * ds.rio.resolution()[1]
        )

        # Aggregate with consistent mask
        for var, clipped in clipped_vars.items():
            weighted_sum = (clipped * cell_area).sum(dim=["x", "y"], skipna=True)
            valid_area = (~clipped.isnull() * cell_area).sum(dim=["x", "y"])

            if var in agg_sum:
                agg_sum[var] += weighted_sum
                agg_area[var] += valid_area
            else:
                agg_sum[var] = weighted_sum
                agg_area[var] = valid_area

        ds.close()



    
        
        # # Loop over variables
        # for ivar,var in enumerate(ds.data_vars):

        #     clipped = ds[var].rio.clip(watershed_proj.geometry, watershed_proj.crs,
        #                                    drop=True, all_touched=False)

        #     # Mask unrealistic or placeholder values
        #     #print(f"BEFORE: {var}: min={float(clipped.min().values):.3e}, max={float(clipped.max().values):.3e}")
        #     #clipped = clipped.where((clipped >= -1e30) & (clipped <= 1e30))
        #     #print(f"AFTER:  {var}: min={float(clipped.min().values):.3e}, max={float(clipped.max().values):.3e}")

        #     # Skip if all NaN
        #     if clipped.isnull().all():
        #         continue

        #     # Compute per-grid-cell area (same shape as data)
        #     cell_area = xr.ones_like(clipped.isel(time=0)) * abs(
        #         ds.rio.resolution()[0] * ds.rio.resolution()[1]
        #     )

        #     # Compute weighted sum and valid area
        #     weighted_sum = (clipped * cell_area).sum(dim=["x", "y"], skipna=True)
        #     valid_area = (~clipped.isnull() * cell_area).sum(dim=["x", "y"])

        #     # Accumulate across files
        #     if var in agg_sum:
        #         agg_sum[var] += weighted_sum
        #         agg_area[var] += valid_area
        #     else:
        #         agg_sum[var] = weighted_sum
        #         agg_area[var] = valid_area

        # ds.close()

    # -----------------------------
    # Combine all variables into DataFrame
    # -----------------------------
    print('')
    if len(agg_sum) > 0:

        # derive spatial average (across all files)
        agg_data = {}
        for var in agg_sum:
            weighted_mean = (agg_sum[var] / agg_area[var]).compute()
            agg_data[var] = weighted_mean

        # check if all values are NaN --> happens when bounding boxes of Netcdf and watershed overlap but no actual data are in watershed area
        all_nan = True
        for var, da in agg_data.items():
            if not np.all(np.isnan(da.values)):
                all_nan = False
                break

        if all_nan:
            
            print("Basin {} covered by some NetCDF files (-i; bbox) but no actual data avaiable there. No output will be written.".format(basin))
            
        else:
            columns_with_units = {}

            for var in agg_data:
                ds_var = ds[var]  # you can use any representative dataset where the var exists
                units = ds_var.attrs.get("units", "")
                if units:
                    columns_with_units[var] = f"{var} [{units}]"
                else:
                    columns_with_units[var] = var
                    
            # Create DataFrame with new column names
            df_out = pd.DataFrame(
                {columns_with_units[var]: agg_data[var].values for var in agg_data},
                index=agg_data[var].time.values
            )

            # check surplus
            surplus_derived = (
                df_out['Domestic_Waste_P [kg ha**-1 yr**-1]']+
                df_out['Fertilizer_P [kg ha**-1 yr**-1]']+
                df_out['Livestock_Manure_P [kg ha**-1 yr**-1]']-
                df_out['Crop_and_Pasture_P_Removal [kg ha**-1 yr**-1]'] )

            if np.any(np.abs(surplus_derived - df_out['P_Surplus [kg ha**-1 yr**-1]']) > 0.00001):
                raise ValueError('P Surplus mismatch')
        
            # Save CSV
            out_filename.parent.mkdir(parents=True, exist_ok=True)
            df_out = df_out.round(5)
            df_out.to_csv(out_filename)
        
            print("Wrote: {}".format(out_filename))

    else:

        print("Basin {} not covered by any data provided in input files (-i). No output will be written.".format(basin))
    
