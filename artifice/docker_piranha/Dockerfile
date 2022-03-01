# start with an image with conda installed
FROM continuumio/miniconda3

# set working directory
WORKDIR /data

# check for updates
RUN apt-get update -y && apt-get upgrade -y

# copy in piranha
RUN git clone https://github.com/aineniamh/piranha.git

# create piranha environment
RUN ls
RUN conda env create -f /data/piranha/environment.yml

# everything from now on will be run in the piranha conda environment
SHELL ["conda", "run", "-n", "piranha", "/bin/bash", "-c"]


# build piranha
WORKDIR /data/piranha
RUN pip install .

#create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

WORKDIR /data/run_data/analysis

# run piranha
ENTRYPOINT piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled
