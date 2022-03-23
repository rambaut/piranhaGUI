# start with an image with conda installed
FROM continuumio/miniconda3 AS compile-image

# set working directory
WORKDIR /data

# check for updates
RUN apt-get update -y && apt-get upgrade -y

# copy in piranha
RUN git clone https://github.com/aineniamh/piranha.git

# create piranha environment
RUN ls
RUN conda env create -f /data/piranha/environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n piranha -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


SHELL ["/bin/bash", "-c"]
# build piranha
WORKDIR /data/piranha
RUN source /venv/bin/activate && pip install --user --no-cache-dir .
#--user .


# build image
FROM debian:buster-slim AS runtime-image

COPY --from=compile-image /root/.local /root/.local

# Copy /venv from the previous stage:
COPY --from=compile-image /venv /venv
#COPY --from=compile-image /opt/conda/ /opt/conda

# create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

# create directory to mount the output directory
RUN mkdir -p /data/run_data/output

WORKDIR /data/run_data/analysis

SHELL ["/bin/bash", "-c"]

# to allow streamed log output
ENV PYTHONUNBUFFERED=1

ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT   source /venv/bin/activate && \
             piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled --outdir /data/run_data/output --overwrite -t ${THREADS}
