import subprocess
import sys
import os
import docker
from datetime import datetime
import PySimpleGUI as sg

from update_log import update_log

def start_rampart(run_path, basecalled_path, client, image, firstPort = 1100, secondPort = 1200, container = None):
    if client == None:
        client = docker.from_env()

    firstPort = str(firstPort)
    secondPort = str(secondPort)
    config_file = 'run_configuration.json'
    containerName = "rampart"

    stop_rampart(client=client,containerName=containerName, container=container)

    ports = {firstPort:firstPort, secondPort:secondPort}
    log_ports = str(ports)
    update_log(f'ports: {log_ports}')

    environment = [f'PORT_ONE={firstPort}', f'PORT_TWO={secondPort}']
    log_environment = str(environment)
    update_log(f'environment variables: {log_environment}')

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')

    container = client.containers.run(image=image, detach=True, name=containerName, ports=ports, environment=environment, volumes=volumes)


    #command = f"docker run -it --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {run_path}:/data/run_data/analysis --volume {basecalled_path}:/data/run_data/basecalled artifice_polio_rampart"
    #print(command)
    #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ rampart_test"
    #command = f"docker run -d --name {containerName} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ emilyscher/polio_rampart"

    #os.system(command)
    return container

def stop_rampart(client = None, containerName='rampart', container = None):
    try:
        container.stop()
        container.remove()
    except:
        if container == None:
            if client == None:
                client = docker.from_env()
            try:
                container = client.containers.get(containerName)
                container.stop()
                container.remove()
            except:
                update_log('tried to stop RAMPART, appears to not be running')
                return None
    update_log('stopped RAMPART')
        #command = f"docker stop {containerName} && docker rm {containerName}"
        #os.system(command)

def check_for_image(client, image_name, font = None):
    if client == None:
        client = docker.from_env()

    try:
        image = client.images.get(image_name)
        #print(image.id)
        return True, client
    except:
        build_ok = sg.popup_ok_cancel('RAMPART docker image not installed yet. Install it? (This may take some time)', font=font)

        if build_ok == 'OK':
            client.images.build(path='./docker_rampart', tag=image_name, rm=True)
            return True, client
        else:
            return False, client


if __name__ == '__main__':
    path = sys.argv[0]
    basecalled_path = sys.argv[1]

    start_rampart(path)
