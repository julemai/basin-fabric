# Example Water Quantity data

These are data of 20 example basins of the Great Lakes Runoff
Intercomparison project (GRIP-GL). Data can be found on HydroHub
(http://hydrohub.org/mips_introduction.html#grip-gl). For citation the
following should be used:

	Mai, J., Shen, H., Tolson, B. A., Gaborit, É., Arsenault, R., Craig,
	J. R., Fortin, V., Fry, L. M., Gauch, M., Klotz, D., Kratzert, F.,
	O’Brien, N., Princz, D. G., Koya, S. R., Roy, T., Seglenieks, F.,
	Shrestha, N. K., Temgoua, A. G. T., Vionnet, V., and Waddell, J. W.:
	(2022). The Great Lakes Runoff Intercomparison Project Phase 4:
	the Great Lakes (GRIP-GL). Hydrology and Earth System
	Sciences, 26(13), 3537–3572.
	http://doi.org/10.5194/hess-26-3537-2022

	Mai, J., Shen, H., Tolson, B. A., Gaborit, E., Arsenault, R., Craig,
	J. R., Fortin, V., Fry, L. M., Gauch, M., Klotz, D., Kratzert, F.,
	O’Brien, N., Princz, D. G., Koya, S. R., Roy, T., Seglenieks, F.,
	Shrestha, N. K., Temgoua, A. G. T., Vionnet, V., and Waddell, J. W.:
	The Great Lakes Runoff Intercomparison Project Phase 4: the Great
	Lakes (GRIP-GL), FRDR [data set and code].
	https://doi.org/10.20383/103.0598

## Basins

The file `basins.csv` lists all 20 example basins with their ID,
latitude and longitude of streamflow gauging station, name of the
station, and gauge station ID.

## Shapefiles

Shapefiles of basin outlines were created by Hongren Shen in GRIP-GL project. Mostly
based on North American routing product v2.1 but with a few extra
(manual) adjustments. Not reproducible.

## Maps

Map of location of 20 example basins in the Great Lakes watershed.

## Forcings

Extracted forcings for each basin from RDRS-v2.1 (downloaded from
caspar-data.ca). Data are clipped to basin domain and then spatially
aggregated to basin domain and temporally aggregated to daily
values. The available time period is Jan 1, 1980 to Dec 31, 2018.

## Observations

Daily streamflow observations for streamflow gauge stations listed
in column `obs_q` in `basins.csv` are retrieved from either Water
Survey Canada's HYDAT database or from USGS. Data are clipped to time
period available for forcings, i.e., Jan 1, 1980 to Dec 31, 2018.

## Attributes

CSV files of static and climate basin attributes are derived based on DEM
(HydroSHEDS), landcover map (NALCMS), soil database (GSDE), and
Regional Deterministic Reanalysis system v2.1 (RDRS-v2.1).
