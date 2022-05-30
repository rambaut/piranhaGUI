# start with ubuntu
FROM ubuntu:14.04.5

WORKDIR data

# pull artifice
RUN apt-get update && apt-get install -y git
RUN apt-get install -y python3 && \
apt-get install -y pip && apt install -y python3.10-venv

SHELL ["/bin/bash", "-c"]

RUN git clone https://github.com/CorwinAnsley/artifice

#WORKDIR data/artifice/
#RUN git pull origin piranhaGUIdev
RUN cd /data/artifice && git checkout piranhaGUIdev

RUN python3 -m pip install --user virtualenv

RUN python3 -m venv env && source env/bin/activate && pip install -r /data/artifice/artifice/requirements.txt

RUN mkdir -p  data/artifice/artifice/linux_build/dist/
WORKDIR /data/artifice/artifice/linux_build/

#ENTRYPOINT source /data/artifice/artifice/linux_build/build_artifice
#ENTRYPOINT ls

# ~REMOVE LATER~ switch branch
