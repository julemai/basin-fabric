#!/bin/bash

# submit with:
#       cd /project/6067703/julemai/src
#       sbatch submit-cedar-validation_experiments.sh

#SBATCH --account=def-julemai                       # def-richard0 # def-julemai                      # rpp-julemai    # your group
#SBATCH --mail-user=juliane.mai@uwaterloo.ca       # email address for notifications
#SBATCH --mail-type=END,FAIL                       # email send only in case of failure

#SBATCH --ntasks=1

##SBATCH --gres=gpu:h100:1                          # REQUIRED FIX to make sure we get a GPU
#SBATCH --gpus-per-node=h100:1                     # optional but ok

#SBATCH --job-name=lstm-eval                       # name of job in queque

## -----------------------------------------------------------------------------------------------
## step 2-4 (evaluate + merge + netcdf)
#SBATCH --time=1-00:00:00                          # time (DD-HH:MM:SS);
#SBATCH --mem=10G                                  # memory; default unit is megabytes
## -----------------------------------------------------------------------------------------------

# job-id  :: ${SLURM_ARRAY_JOB_ID}
# task-id :: ${SLURM_ARRAY_TASK_ID}

# Load some modules
module load StdEnv/2023 gcc/12.3 netcdf/4.9.2 gdal/3.7.2 mpi4py/3.1.4 proj/9.2.0 geos/3.12.0 nco/5.1.7 python/3.11.5

# Load Python env
source /project/6067703/julemai/env-3.11-cuda/bin/activate

# Do evaluation
cd /project/6067703/julemai/src


# debugging
#
echo ""
echo "---------------------------------------------"
echo "Debugging: "
echo "---------------------------------------------"
python - << 'EOF'
import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("Device count:", torch.cuda.device_count())
print("GPU name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")
print("Supported architectures:", torch.cuda.get_arch_list())
EOF
echo "---------------------------------------------"





# # evaluate all models on a new region (north-america-mai)                                                                                      # --------- step 2-3 ---------------
# python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v2      -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071584   
# python 14_run_validation_experiments.py -s north-america-mai -u grip-gl-mai-v3      -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071556
# python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v1        -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071575
# python 14_run_validation_experiments.py -s north-america-mai -u conus-zhi-v2        -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071610
# python 14_run_validation_experiments.py -s north-america-mai -u camels-us-newman-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1           # (2575) 2h/seed      2d   37071617


# # evaluate all regions with new model (north-america-mai-v1)                                                                                   # --------- step 2-3 ---------------
# python 14_run_validation_experiments.py -s wisconsin-lewis      -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wisconsin-lewis-v1         #   (47) 5min/seed  1.0h  DONE interactively
# python 14_run_validation_experiments.py -s lake-erie-us-gaffney -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f lake-erie-us-gaffney-v1    #   (78) 9min/seed  2.0h  DONE interactively
# python 14_run_validation_experiments.py -s ontario-zhi          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f ontario-zhi-v1             #  (361) ??/seed   10.0h  1.0GB  37071442
# python 14_run_validation_experiments.py -s grip-gl-mai          -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f grip-gl-mai-v3             #  (212) ??/seed    2.5h  1.0GB  37071384
# python 14_run_validation_experiments.py -s conus-zhi            -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f conus-zhi-v1               #  (513) ??/seed   12.0h  1.5GB  37071357
# python 14_run_validation_experiments.py -s camels-us-newman     -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f camels-us-newman-v1        #  (671) ??/seed    8.0h  1.5GB  37071314
# python 14_run_validation_experiments.py -s north-america-mai    -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f north-america-mai-v1       # (2575) 3h/seed      3d  ???   37071252


# evaluate all models on a new region (wrtdsk-mai)                                                                             # --------- step 2-4 ---------------
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u grip-gl-mai-v2       -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11773491
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u grip-gl-mai-v3       -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11773745
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u conus-zhi-v1         -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11773921
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u conus-zhi-v2         -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11774126
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11774310
#python 14_run_validation_experiments.py -s wrtdsk-mai  -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wrtdsk-mai-v1       #  (660)   4.0h  6GB  11583881


# evaluate all models on a new region (wrtdsk-mai)                                                                             # --------- step 2-4 ---------------
#python 14_run_validation_experiments.py -s wq-us-chang -u grip-gl-mai-v2       -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11774853
#python 14_run_validation_experiments.py -s wq-us-chang -u grip-gl-mai-v3       -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11774879
#python 14_run_validation_experiments.py -s wq-us-chang -u conus-zhi-v1         -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11774965
#python 14_run_validation_experiments.py -s wq-us-chang -u conus-zhi-v2         -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11775064
#python 14_run_validation_experiments.py -s wq-us-chang -u camels-us-newman-v1  -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11775118
#python 14_run_validation_experiments.py -s wq-us-chang -u north-america-mai-v1 -p 1980-01-01:2018-12-31 -f wq-us-chang-v1      # (2387)   1d  	10GB   11603769

