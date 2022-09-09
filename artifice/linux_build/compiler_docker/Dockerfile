# start with ubuntu
FROM ubuntu:20.04

WORKDIR data

ENV DEBIAN_FRONTEND=noninteractive
# pull artifice
RUN apt-get update && apt-get install -y git
RUN apt-get install -y python3 && \
apt-get install -y python3-pip && \
apt install -y python3-venv && apt-get install -y python3-tk

SHELL ["/bin/bash", "-c"]
RUN git clone https://github.com/CorwinAnsley/artifice

# ~REMOVE LATER~ switch branch
#RUN git pull origin piranhaGUIdev
RUN cd /data/artifice && git checkout dev

RUN python3 -m pip install --user virtualenv

RUN python3 -m venv env && source env/bin/activate && pip install -r /data/artifice/artifice/requirements.txt && pip install tk

RUN mkdir -p  data/artifice/artifice/linux_build/dist/
WORKDIR /data/artifice/artifice/linux_build/

#ENTRYPOINT source /data/env/bin/activate && source /data/artifice/artifice/linux_build/build_artifice
ENTRYPOINT source /data/env/bin/activate && source /data/artifice/artifice/linux_build/build_artifice && source /data/artifice/artifice/linux_build/create_deb_package
#ENTRYPOINT ls
