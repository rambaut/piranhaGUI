# start with image with rampart and polio protocol installed
FROM emilyscher/polio_rampart

#create directory to mount the basecalled directory
RUN mkdir -p /data/run_data/basecalled

#run rampart
ENTRYPOINT node /data/rampart/rampart.js --protocol /data/realtime-polio/rampart/ --ports ${PORT_ONE} ${PORT_TWO} --basecalledPath /data/run_data/basecalled --clearAnnotated
