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

# everything from now on will be run in the artic-rampart conda environment
SHELL ["conda", "run", "-n", "piranha", "/bin/bash", "-c"]

# build piranha
RUN pip install .

#create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

# run rampart
ENTRYPOINT piranha -i /data/run_data/basecalled -b ${BARCODES}
