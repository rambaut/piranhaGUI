import subprocess
import sys
import os
import docker
from datetime import datetime

def start_rampart(run_path, basecalled_path, client, firstPort = 1100, secondPort = 1200, container = None):
    if client == None:
        client = docker.from_env()

    firstPort = str(firstPort)
    secondPort = str(secondPort)
    config_file = 'run_configuration.json'
    containerName = "rampart"

    stop_rampart(containerName=containerName, container=container)

    ports = {firstPort:firstPort, secondPort:secondPort}
    environment = [f'PORT_ONE={firstPort}', f'PORT_TWO={secondPort}']
    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    container = client.containers.run(image='artifice_polio_rampart', detach=True, name=containerName, ports=ports, environment=environment, volumes=volumes)
    print('s')

    #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {run_path}:/data/run_data/analysis --volume {basecalled_path}:/data/run_data/basecalled artifice_polio_rampart"

    #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ rampart_test"
    #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ emilyscher/polio_rampart"

    #os.system(command)
    return client, container

def stop_rampart(containerName='rampart', container = None):
        try:
            container.stop(containerName)
            container.remove(containerName)
        except:
            command = f"docker stop {containerName} && docker rm {containerName}"
            os.system(command)

    #command = "docker stop rampart && docker rm rampart"
    #os.system(command)


if __name__ == '__main__':
    path = sys.argv[0]
    basecalled_path = sys.argv[1]

    start_rampart(path)
