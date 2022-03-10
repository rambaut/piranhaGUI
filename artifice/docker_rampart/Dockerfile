# start with an image with conda installed
FROM continuumio/miniconda3

# set working directory
WORKDIR /data

# install gcc/make for porechop
RUN apt-get update -y && apt-get upgrade -y
RUN apt install build-essential -y --no-install-recommends

# copy in protocol files
RUN git clone https://github.com/polio-nanopore/realtime-polio

# create rampart environment
RUN ls
RUN conda env create -f /data/realtime-polio/environment.yml

# everything from now on will be run in the realtime-polio conda environment
SHELL ["conda", "run", "--no-capture-output", "-n", "realtime-polio", "/bin/bash", "-c"]

# install rampart
RUN git clone https://github.com/artic-network/rampart.git

WORKDIR /data/rampart

# update npm, install npm packages, build rampart
RUN npm install
RUN npm run build

WORKDIR /data/run_data/analysis

#set environment variable PYTHONUNBUFFERED to allow unbuffered log output
ENV PYTHONUNBUFFERED=1

#create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

#run rampart
ENTRYPOINT node /data/rampart/rampart.js --protocol /data/realtime-polio/rampart/ --ports ${PORT_ONE} ${PORT_TWO} --basecalledPath /data/run_data/basecalled --clearAnnotated
