# Data

This folder might hold data retrieved or generated.

## Provincial (Stream) Water Quality Monitoring Network (PWQMN) data
Data for water quality variables such as nitrate and phosphor. The
data need to be manually downloaded through:
https://greatlakesdatastream.ca/explore/#/dataset/f3877597-9114-4ace-ad6f-e8a68435c0ba/

Then click the download button appearing on that website.
Name: `Provincial_Water_Quality_Monitoring_Network_PWQMN.csv` (data)
Name: `Provincial_Water_Quality_Monitoring_Network_PWQMN_metadata.csv`
(metadata)


The datafile is a comma-separated file but several entries contain
commas themselves. The entry is then in double-quotes, e.g.,
123,"ABC, DEV 23",345,534.202,"abd,dged,sdg",2,4

The handling of this in the code takes ages. Hence, we clean the data
from those double-quotes and commas and replace them by semi-colons,
e.g.,
123,ABC;DEV;23,345,534.202,abd;dged;sdg,2,4
using:

`awk -F'"' -v OFS='' '{ for (i=2; i<=NF; i+=2) gsub(",", ";", $i) } 1' Provincial_Water_Quality_Monitoring_Network_PWQMN.csv > Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv`

**Download link (preprocessed data by Julie)**:  http://juliane-mai.com/data_nandita/Provincial_Water_Quality_Monitoring_Network_PWQMN_cleaned.csv
