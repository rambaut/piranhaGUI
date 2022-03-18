# start with an image with conda installed
FROM continuumio/miniconda3 AS compile-image

# set working directory
WORKDIR /data

# check for updates
RUN apt-get update -y && apt-get upgrade -y

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# copy in piranha
RUN git clone https://github.com/aineniamh/piranha.git

# create piranha environment
RUN ls
RUN conda env create -f /data/piranha/environment.yml

# everything from now on will be run in the piranha conda environment
SHELL ["conda", "run", "--no-capture-output", "-n", "piranha", "/bin/bash", "-c"]

# build piranha
WORKDIR /data/piranha
RUN pip install .
#--user .

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

# build image
FROM continuumio/miniconda3 AS runtime-image

COPY --from=compile-image /root/.local /root/.local

# Copy /venv from the previous stage:
COPY --from=compile-image /venv /venv
#COPY --from=compile-image /opt/conda/ /opt/conda

# create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

# create directory to mount the output directory
RUN mkdir -p /data/run_data/output

WORKDIR /data/run_data/analysis

SHELL ["/bin/bash", "-c", "source", "/venv/bin/activate", "&&"]

ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH
# run piranha
#source /venv/bin/activate && \
ENTRYPOINT piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled --outdir /data/run_data/output --overwrite -t ${THREADS}
