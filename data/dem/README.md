# list all BIL zip files
files=$( \ls *_dem_3s_zip_bil/*.zip  )

# create folders to unzip all BIL zip files
for ff in $files ; do mkdir $( echo $ff | cut -d . -f 1 ) ; done

# unzip all BIL zip files
for ff in $files ; do dd=$( echo $ff | cut -d . -f 1 ) ; unzip $ff -d
$dd ; done

# merge them (rio only available in some Python envs)
pyenv activate 3.8.5/envs/env-3.8.5-ravenpy-new
rio merge *_dem_3s_zip_bil/*/*.bil na_ca_dem_3s.tif

# create slope file
gdaldem slope -s 111120 na_ca_dem_3s.tif na_ca_dem_3s-slope.tif
