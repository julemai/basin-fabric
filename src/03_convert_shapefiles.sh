#!/bin/bash

# Copyright 2022 Juliane Mai - juliane.mai(at)uwaterloo.ca
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
#
# pyenv activate env-3.8.5-ravenpy-new
# ./03_convert_shapefiles.sh -s conus-zhi
# ./03_convert_shapefiles.sh -s grip-gl-mai
# ./03_convert_shapefiles.sh -s camels-us-newman
# ./03_convert_shapefiles.sh -s lake-erie-us-gaffney
# ./03_convert_shapefiles.sh -s prairie-canada-mai
# ./03_convert_shapefiles.sh -s prairie-canada-downstream-mai


set -e

prog=$0
pprog=$(basename ${prog})
dprog=$(dirname ${prog})
isdir=${PWD}
pid=$$

case_study="None"
while getopts "hs:" Option ; do
    case ${Option} in
        h) exit 0;;
        s) case_study="${OPTARG}";;
        *) printf "Error ${pprog}: unimplemented option.\n\n";  exit 1;;
    esac
done
shift $((${OPTIND} - 1))

# Check if case_study is given
if [[ ${case_study} == 'None' ]] ; then
    printf "Error ${pprog}: Case study (-s) must be given.\n"
    exit 1
fi
case ${case_study} in
    'conus-zhi')            	       ok='True' ;;
    'grip-gl-mai')          	       ok='True' ;;
    'camels-us-newman')     	       ok='True' ;;
    'lake-erie-us-gaffney') 	       ok='True' ;;
    'prairie-canada-mai')              ok='True' ;;
    'prairie-canada-downstream-mai')   ok='True' ;;
    *) printf "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai', 'camels-us-newman', 'lake-erie-us-gaffney'.\n\n"; exit 1;;
esac


if [[ ${case_study} == 'conus-zhi' ]] ; then
    # conus-zhi
    region_tag='conus-zhi'

    basins=$(  \ls ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 )
    nbasins=$( \ls ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_*.shp | rev | cut -d '/' -f 1 | rev | cut -d '_' -f 2 | cut -d '.' -f 1 | wc -l )
else
    if [[ ${case_study} == 'grip-gl-mai' ]] ; then
	# grip-gl-mai
	region_tag='grip-gl-mai'

	basins=$(  \ls ${dprog}/../regions/${region_tag}/shapefiles_raw/*/*.shp | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1 )
	nbasins=$( \ls ${dprog}/../regions/${region_tag}/shapefiles_raw/*/*.shp | rev | cut -d '/' -f 1 | rev | cut -d '.' -f 1 | wc -l )
    else
	if [[ ${case_study} == 'camels-us-newman' ]] ; then
	    # camels-us-newman
	    region_tag='camels-us-newman'

	    basins=$(  cat ${dprog}/../regions/${region_tag}/basins.csv | cut -d ',' -f 1 | grep -v 'id' )
	    nbasins=$( cat ${dprog}/../regions/${region_tag}/basins.csv | cut -d ',' -f 1 | grep -v 'id' | wc -l )
	    nbasins=$( echo ${nbasins} )
	else
	    if [[ ${case_study} == 'lake-erie-us-gaffney' ]] ; then
		# lake-erie-us-gaffney
		region_tag='lake-erie-us-gaffney'

		basins=$(  \ls ${dprog}/../regions/${region_tag}/20230828_Katie_Shape_files_raw/*/*.shp | rev | cut -d '/' -f 2 | rev )
		nbasins=$( \ls ${dprog}/../regions/${region_tag}/20230828_Katie_Shape_files_raw/*/*.shp | rev | cut -d '/' -f 2 | rev | wc -l )
	    else
		if [[ ${case_study} == 'prairie-canada-mai' ]] ; then
		    # entire drainage areas
		    # prairie-canada-mai   
		    region_tag='prairie-canada-mai'

		    # 2024-07-23 - basins with entire drainage area - resolved gaps and overlapping areas
		    basins=$(  cat ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_bsns25_attrb.csv | cut -d ',' -f 2 | grep -v 'stnid' | grep -v "^$" )
		    nbasins=$( cat ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_bsns25_attrb.csv | cut -d ',' -f 2 | grep -v 'stnid' | grep -v "^$" | wc -l )

		else

		    if [[ ${case_study} == 'prairie-canada-downstream-mai' ]] ; then
			# only downstream portions of drainage areas
			# prairie-canada-downstream-mai    
			region_tag='prairie-canada-downstream-mai'


			# 2024-07-23 - basins with downstream drainage area - resolved gaps and overlapping areas
			basins=$(  cat ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_bsns25_attrb.csv | cut -d ',' -f 2 | grep -v 'stnid' | grep -v "^$" )
			nbasins=$( cat ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_bsns25_attrb.csv | cut -d ',' -f 2 | grep -v 'stnid' | grep -v "^$" | wc -l )
		    else
			echo "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai', 'camels-us-newman', 'lake-erie-us-gaffney', 'prairie-canada-mai', 'prairie-canada-downstream-mai'.\n\n"
			exit 1
		    fi
		fi
	    fi
	fi
    fi
fi


# create directory
if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles ] ; then
    mkdir ${dprog}/../regions/${region_tag}/shapefiles
fi

cc=1
for bb in ${basins} ; do

    echo "  "
    echo "${bb} (${cc} of ${nbasins})"

    # create directory
    if [ ! -e ${dprog}/../regions/${region_tag}/shapefiles/${bb} ] ; then
    	mkdir ${dprog}/../regions/${region_tag}/shapefiles/${bb}
    fi

    if [[ ${case_study} == 'conus-zhi' ]] ; then
	# conus-zhi
	# convert Wei's shapefile with weird projection into standard one (add ESPG and save only longest feature)
	python additional_processing/convert_coords_to_espg.py \
	       -i ${dprog}/../regions/${region_tag}/20230612_Wei_selected_US_sites_shapefile/b_${bb}.shp \
	       -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
	       -e 4326
    else
	if [[ ${case_study} == 'grip-gl-mai' ]] ; then
	    # grip-gl-mai
	    # convert grip-gl-mai shapefile with into standard one (save only longest feature; add ESPG; but it's actually just a rename...)
	    python additional_processing/convert_coords_to_espg.py \
		   -i ${dprog}/../regions/${region_tag}/shapefiles_raw/${bb}/${bb}.shp \
		   -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
		   -e 4326
	else
	    if [[ ${case_study} == 'camels-us-newman' ]] ; then
		# camels-us-newman
		# extract basins from shapefile containing all basins and convert into standard one (save only longest feature; add ESPG)
		if [ ${bb::1} == '0' ] ; then
		    # first character is '0' --> remove that '0'
		    basin_id_in_shp=$( echo ${bb} | cut -c 2- )
		else
		    basin_id_in_shp=${bb}
		fi
		python additional_processing/convert_coords_to_espg.py \
		       -i ${dprog}/../regions/${region_tag}/HCDN_nhru_final_671/HCDN_nhru_final_671.shp \
		       -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
		       -x "hru_id=${basin_id_in_shp}" \
		       -e 4326
	    else
		if [[ ${case_study} == 'prairie-canada-mai' ]] ; then
		    # prairie-canada-mai
		    # extract basins from shapefile containing all basins and convert into standard one (save only longest feature; add ESPG)
		   
		    basin_id_in_shp=${bb}

		    # # 2024-06-14 - basins with ENTIRE drainage area - has lots of gaps and overlapping areas
		    # python additional_processing/convert_coords_to_espg.py \
		    # 	   -i ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240614/NC_bsns_25finalsubs.shp \
		    # 	   -o ${dprog}/../regions/${region_tag}/shapefiles/${bb}/${bb}_lp \
		    # 	   -x "stnid=${basin_id_in_shp}=str" \
		    # 	   -e 4326

		    # 2024-07-23 - basins with ENTIRE drainage area - resolved gaps and overlapping areas
		    python additional_processing/convert_coords_to_espg.py \
		    	   -i ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_merit_135bsns.shp \
		    	   -o ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/${bb}/${bb}_lp \
		    	   -x "STATION_NU=${basin_id_in_shp}=str" \
		    	   -e 4326

		else
		    if [[ ${case_study} == 'prairie-canada-downstream-mai' ]] ; then
			# prairie-canada-downstream-mai
			# extract basins from shapefile containing all basins and convert into standard one (save only longest feature; add ESPG)
			
			basin_id_in_shp=${bb}
			
			# 2024-07-23 - basins with only DOWNSTREAM drainage area - resolved gaps and overlapping areas
			#  --> this file has basin 06CD002 with "island": shapefiles_prairie-canada-mai_20240723/NC_merit_re135bsns.shp
			#  --> this file resolved that:                   shapefiles_prairie-canada-mai_20240723/NC_re135bsns_mJ.shp
			python additional_processing/convert_coords_to_espg.py \
			       -i ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/NC_re135bsns_mJ.shp \
			       -o ${dprog}/../regions/${region_tag}/shapefiles_prairie-canada-mai_20240723/${bb}/${bb}_lp \
			       -x "STATION_NU=${basin_id_in_shp}=str" \
			       -e 4326
		    else
			if [[ ${case_study} == 'lake-erie-us-gaffney' ]] ; then
			    
			    # find basin name in basins.csv
			    bb_parts=$( echo ${bb} | tr '_' ' ' )
			    found=False
			    while read -r line; do
				good='True'
				for part in ${bb_parts} ; do
				    if [[ ${line} != *"${part}"* ]] ; then
					#echo "Not there!"
					good='False'
				    fi
				done
				if [[ ${good} == 'True' ]] ; then
				    ibb=$( echo ${line} | cut -d ',' -f 1 )
				    echo "Found basin ${bb} as ID ${ibb}"
				fi
			    done < ${dprog}/../regions/${region_tag}/basins.csv
			    
			    python additional_processing/convert_coords_to_espg.py \
				   -i ${dprog}/../regions/${region_tag}/20230828_Katie_Shape_files_raw/${bb}/area-of-interest.shp \
				   -o ${dprog}/../regions/${region_tag}/shapefiles/${ibb}/${ibb}_lp \
				   -x "FID=0" \
				   -e 4326
			    
			else
			    echo "Error ${pprog}: Option (-s) needs to be one of the following: 'conus-zhi', 'grip-gl-mai', 'camels-us-newman'.\n\n"
			    exit 1
			fi
		    fi
		fi
	    fi
	fi
    fi
    
    cc=$(( cc+1 ))
    
done

exit 0
