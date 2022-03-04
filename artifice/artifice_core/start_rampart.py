import sys
import os
import docker
from datetime import datetime
import PySimpleGUI as sg
from webbrowser import open_new_tab
import requests
import json
from time import sleep, time
import re

from artifice_core.update_log import update_log
import artifice_core.consts
import artifice_core.view_barcodes_window

def start_rampart(run_path, basecalled_path, client, image, firstPort = 1100, secondPort = 1200, container = None):
    if client == None:
        client = docker.from_env()

    firstPort = str(firstPort)
    secondPort = str(secondPort)
    config_file = 'run_configuration.json'
    containerName = "rampart"

    stop_docker(client=client,containerName=containerName, container=container)

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

def stop_docker(client = None, containerName='rampart', container = None):
    if containerName == 'rampart':
        tool_name = 'RAMPART'
    elif containerName == 'piranha':
        tool_name = 'PIRANHA'
    else:
        tool_name = '<unknown application>'

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
                update_log(f'tried to stop {tool_name}, appears to not be running')
                return None
    update_log(f'stopped {tool_name}')
        #command = f"docker stop {containerName} && docker rm {containerName}"
        #os.system(command)

def return_log(container, since):
    #print(since)
    #try:
        #log_str = next(log)
    log_str = container.logs(since=since)
    #remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    piranha_output = ansi_escape.sub('', log_str.decode('utf-8'))
    #except:
    #    piranha_output = ''
    #finally:
    since = datetime.now()

    return piranha_output, since

def check_for_image(client, image_name, font = None):
    if client == None:
        client = docker.from_env()

    try:
        image = client.images.get(image_name)
        update_log('confirmed image is installed')
        #print(image.id)
        return True, client
    except:
        build_ok = sg.popup_ok_cancel('RAMPART docker image not installed yet. Install it? (This may take some time)', font=font)

        if build_ok == 'OK':
            #client.images.build(path='./docker_rampart', tag=image_name, rm=True)
            client.images.pull(image_name)
            return True, client
        else:
            return False, client

def check_for_docker(font = None, docker_url = 'https://docs.docker.com/get-docker/'):
    try:
        info = docker.from_env().info()
        return True
    except:
        open_site = sg.popup_ok_cancel('Docker client not found. Please install docker and restart artifice. Press OK below to open docker site in browser', font = font)
        if open_site == 'OK':
            open_new_tab('https://docs.docker.com/get-docker/')

        return False

#makes sure run is valid for running rampart/piranha and creates run_configuration json
def prepare_run(run_info, runs_dir = artifice_core.consts.RUNS_DIR, font = None):
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')
    title = run_info['title']
    update_log(f'preparing run: "{title}"')
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception(f'Invalid samples file')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')


    config_path = runs_dir+'/'+title+'/run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dump(run_configuration, file)

    artifice_core.view_barcodes_window.check_barcodes(run_info,font=font)

def launch_rampart(run_info, client, firstPort = 1100, secondPort = 1200, runs_dir = artifice_core.consts.RUNS_DIR, font = None, container = None):
    prepare_run(run_info,runs_dir=runs_dir,font=font)

    basecalled_path = run_info['basecalledPath']
    run_path = runs_dir+'/'+run_info['title']
    container = start_rampart(run_path, basecalled_path, client, artifice_core.consts.RAMPART_IMAGE, firstPort = firstPort, secondPort = secondPort, container=container)

    iter = 0
    while True:
        sleep(0.1)
        iter += 1
        if iter > 100:
            raise Exception('Something went wrong launching RAMPART')
        try:
            rampart_running = check_rampart_running()
            if rampart_running:
                return container
        except:
            pass

def check_rampart_running():
    try:
        r = requests.get(f'http://localhost:{artifice_core.consts.RAMPART_PORT_1}')
        if r.status_code == 200:
            update_log(f'detected RAMPART running on port: {artifice_core.consts.RAMPART_PORT_1}')
            return True
        else:
            return False
    except:
        return False

if __name__ == '__main__':
    path = sys.argv[0]
    basecalled_path = sys.argv[1]

    start_rampart(path)
