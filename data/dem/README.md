# Download
DEM data: HydroSHEDS DEM 3s<br>
https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAyFvMjPf92oRrw-I-ydyova/HydroSHEDS_DEM/DEM_3s_BIL

--> na_dem_3s_zip_bil

# Download via command line

```
wget https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAWC8iv3z_L976IGLBUZOFFa/HydroSHEDS_DEM/DEM_3s_BIL/na_dem_3s_zip_bil?dl=1
mv 'na_dem_3s_zip_bil?dl=1' na_dem_3s_zip_bil.zip
unzip na_dem_3s_zip_bil.zip

mkdir na_dem_3s_zip_bil
mv n*w*_dem_bil.zip na_dem_3s_zip_bil/.
```

Proceed with below.

```bash
# list all BIL zip files
files=$( \ls *_dem_3s_zip_bil/*.zip  )

# create folders to unzip all BIL zip files
for ff in $files ; do mkdir $( echo $ff | cut -d . -f 1 ) ; done

# unzip all BIL zip files
for ff in $files ; do dd=$( echo $ff | cut -d . -f 1 ) ; unzip $ff -d $dd ; done

# merge them (rio only available in some Python envs)
# load Python environment that contains rasterio:
pyenv activate 3.8.5/envs/env-3.8.5-ravenpy-new
source env-3.10/bin/activate
rio merge *_dem_3s_zip_bil/*/*.bil na_ca_dem_3s.tif

# create slope file
gdaldem slope -s 111120 na_ca_dem_3s.tif na_ca_dem_3s-slope.tif
```

# resulting files expected in this folder
- na_ca_dem_3s-slope.tif
- na_ca_dem_3s.hdr
- na_ca_dem_3s.prj
- na_ca_dem_3s.tif
- na_ca_dem_3s.tif.aux.xml
- na_dem_3s_zip_bil.zip
