# start with an image with conda installed
FROM dmmalone/rampart:0.0.4

# set working directory
WORKDIR /data

# copy in protocol files
RUN git clone https://github.com/polio-nanopore/realtime-polio

# everything from now on will be run in the realtime-polio conda environment
SHELL ["conda", "run", "--no-capture-output", "-n", "artic-rampart", "/bin/bash", "-c"]

WORKDIR /data/run_data/analysis

# set environment variable PYTHONUNBUFFERED to allow unbuffered log output for artifice
ENV PYTHONUNBUFFERED=1

# create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

# run rampart
#ENTRYPOINT rampart --protocol /data/realtime-polio/rampart/ --ports ${PORT_ONE} ${PORT_TWO} --basecalledPath /data/run_data/basecalled --clearAnnotated
ENTRYPOINT rampart --ports ${PORT_ONE} ${PORT_TWO} --basecalledPath /data/run_data/basecalled --clearAnnotated --referencesPath /data/realtime-polio/rampart/references.fasta
