import subprocess
import sys
import os
from datetime import datetime

def start_rampart(path, firstPort = str(1100), secondPort = str(1200)):

    containerName = "rampart"

    command = "sudo docker stop rampart && sudo docker rm rampart"
    os.system(command)

    command = "sudo docker run -d --name "+containerName+" -p "+secondPort+":"+secondPort+" -p "+firstPort+":"+firstPort+" -e PORT_ONE="+firstPort+" -e PORT_TWO="+secondPort+" -e RUN_PATH=/data/run_data/ --volume "+path+":/data/run_data/ emilyscher/polio_rampart"
    os.system(command)

def stop_rampart():
    command = "sudo docker stop rampart && sudo docker rm rampart"
    os.system(command)
    
if __name__ == '__main__':
    path = sys.argv[-1]

    start_rampart(path)
