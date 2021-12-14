import subprocess
import sys
import os
from datetime import datetime

def start_rampart(path, firstPort = 1100, secondPort = 1200, test = False):
    firstPort = str(firstPort)
    secondPort = str(secondPort)
    containerName = "rampart"

    command = "docker stop rampart && docker rm rampart"
    os.system(command)
    if test:
        #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {path}:/data/run_data/ rampart_test"
        command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ rampart_test"
    else:
        command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ emilyscher/polio_rampart"
        #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {path}:/data/run_data/ emilyscher/polio_rampart"
        #command = "docker run -d --name "+containerName+" -p "+firstPort+":"+firstPort+" -p "+secondPort+":"+secondPort+" -e PORT_ONE="+firstPort+" -e PORT_TWO="+secondPort+" --volume "+path+":/data/run_data/ emilyscher/polio_rampart"
    print(command)
    os.system(command)

def stop_rampart():
    command = "docker stop rampart && docker rm rampart"
    os.system(command)

if __name__ == '__main__':
    path = sys.argv[-1]

    start_rampart(path)
