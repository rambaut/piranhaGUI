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
import multiprocessing
import traceback

from artifice_core.update_log import update_log
import artifice_core.consts as consts
import artifice_core.view_barcodes_window

def start_rampart(run_path, basecalled_path, client, image, firstPort = 1100, secondPort = 1200, container = None, protocol_path = None,):
    if client == None:
        client = docker.from_env()

    firstPort = str(firstPort)
    secondPort = str(secondPort)
    config_file = 'run_configuration.json'
    container_name = "rampart"

    stop_docker(client=client,container_name=container_name, container=container)

    ports = {firstPort:firstPort, secondPort:secondPort}
    log_ports = str(ports)
    update_log(f'ports: {log_ports}')

    environment = [f'PORT_ONE={firstPort}', f'PORT_TWO={secondPort}']
    log_environment = str(environment)
    update_log(f'environment variables: {log_environment}')

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    if protocol_path != None or protocol_path != 'default':
        volumes.append(f'{protocol_path}:/data/run_data/protocol')
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')
    test = False

    if test:
        command = f"docker run -d --name {container_name} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {run_path}:/data/run_data/analysis --volume {basecalled_path}:/data/run_data/basecalled {artifice_core.consts.RAMPART_IMAGE                      }"
        print(command)
        os.system(command)
        client = None

    else:
        container = client.containers.run(image=image, detach=True, name=container_name, ports=ports, environment=environment, volumes=volumes)

    #command = f"docker run -it --name {container_name} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} --volume {run_path}:/data/run_data/analysis --volume {basecalled_path}:/data/run_data/basecalled artifice_polio_rampart"
    #print(command)
    #command = f"docker run -d --name {container_name} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ rampart_test"
    #command = f"docker run -d --name {container_name} -p {secondPort}:{secondPort} -p {firstPort}:{firstPort} -e PORT_ONE={firstPort} -e PORT_TWO={secondPort} -e RUN_PATH=/data/run_data/ --volume {path}:/data/run_data/ emilyscher/polio_rampart"

    #os.system(command)
    return container

# Stops docker container corresponding to given tool
def stop_docker(client = None, container_name='rampart', container = None):
    if container_name == 'rampart':
        tool_name = 'RAMPART'
    elif container_name == 'piranha':
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
                container = client.containers.get(container_name)
                container.stop()
                container.remove()
            except:
                update_log(f'tried to stop {tool_name}, appears to not be running')
                return None
    update_log(f'stopped {tool_name}')

#put the streamed output of container log into queue
def queue_log(log, queue):
    while True:
        log_str = ''

        try:
            log_str = next(log)
        except StopIteration:
            log_output ='###CONTAINER STOPPED###\n'
            queue.put(log_output)
            return

        #remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        log_output = ansi_escape.sub('', log_str.decode('utf-8'))

        if len(log_output) > 0:
            queue.put(log_output)

#check image exists for given tag
def check_for_image(client, image_tag, popup = True, tool_name = 'RAMPART'):
    if client == None:
        client = docker.from_env()

    try:
        image = client.images.get(image_tag)
        update_log(f'confirmed image: {image_tag} is installed')
        #print(image.id)
        if popup:
            build_ok = sg.popup_ok_cancel(f'{tool_name} docker image installed, check for updates?')
            if build_ok != 'OK':
                return True, client
        else:
            return True, client

    except:
        if popup:
            build_ok = sg.popup_ok_cancel(f'{tool_name} docker image not installed yet. Install it? (This may take some time)')
        else:
            return False, client

    if build_ok == 'OK':
        #client.images.build(path='./docker_rampart', tag=image_tag, rm=True)
        client.images.pull(image_tag)
        return True, client
    else:
        return False, client

# Checks dockerhub repo to see if there has been an update to image, returns True if so
def check_for_image_updates(client, image_tag):
    if client == None:
        client = docker.from_env()
    update_log(f'checking for updates to: {image_tag}')
    try:
        api_url =  f'https://hub.docker.com/v2/repositories/{image_tag}/tags'

        response = requests.get(api_url)
        tags = response.json()

        latest_version = None
        #search results for latest tag
        for tag in tags['results']:
            if tag['name'] == 'latest':
                #print(tag)
                latest_date = str(tag['last_updated'])[0:10]
                latest_digest = tag['digest']
        
        for tag in tags['results']:
            if not tag['name'] == 'latest': 
                digest = tag['digest']

                if digest == latest_digest:
                    latest_version = tag['name']
                    break
        
        #print(latest_digest)
        trunc_latest_digest = latest_digest.split('sha256:')[-1]

        image = client.images.get(image_tag)
        new_version_available = False
        try:
            local_digest = image.attrs['RepoDigests'][0]

            if len(local_digest) > 5:
                trunc_local_digest = local_digest.split('sha256:')[-1]
                if trunc_local_digest != trunc_latest_digest:
                    new_version_available = True
            else:
                raise Exception
        except:
            local_date = str(image.attrs['Created'])[0:10]
            if local_date != latest_date:
                new_version_available = True

        if new_version_available:
            update_log(f'updated version of image, {image_tag}, found: {latest_version}')
            return True, latest_version
        else:
            update_log(f'confirmed image, {image_tag}, is up to date:  {latest_version}')
            return False, latest_version
    
    except:
        update_log('error looking for updates')
        update_log(traceback.format_exc())
        return False, None


# Checks if docker is installed
def check_for_docker(docker_url = 'https://docs.docker.com/get-docker/', popup = True):
    try:
        info = docker.from_env().info()
        return True
    except:
        if popup:
            open_site = sg.popup_ok_cancel('Docker client not found. Please install docker and restart artifice. Press OK below to open docker site in browser')
            if open_site == 'OK':
                open_new_tab(docker_url)

        return False

#makes sure run is valid for running rampart/piranha and creates run_configuration json
def prepare_run(run_info, runs_dir = None, output = False):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR

    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')
    title = run_info['title']
    update_log(f'preparing run: "{title}"')
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception(f'Invalid samples file')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid sequencing data directory')

    if output:
        if 'outputPath' not in run_info or os.path.isdir(run_info['outputPath']) == False:
            raise Exception('Invalid output directory')

    config_path = runs_dir / title / 'run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dump(run_configuration, file)

    artifice_core.view_barcodes_window.check_barcodes(run_info)

def launch_rampart(run_info, client, firstPort = 1100, secondPort = 1200, runs_dir = None, container = None, protocol_path = None):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR

    prepare_run(run_info,runs_dir=runs_dir)

    basecalled_path = run_info['basecalledPath']
    run_path = runs_dir / run_info['title']
    container = start_rampart(run_path, basecalled_path, client, consts.RAMPART_IMAGE, firstPort = firstPort, secondPort = secondPort, container=container, protocol_path=protocol_path)
    """
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
    """
    return container

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

#check container exists for given name
def check_container(container_name, client = None):
    if client == None:
        client = docker.from_env()

    #client.containers.prune()

    try:
        client.containers.get(container_name)
        return True
    except docker.errors.NotFound:
        return False


if __name__ == '__main__':
    path = sys.argv[0]
    basecalled_path = sys.argv[1]

    start_rampart(path)

# takes the optional arguments in run_info and converts them to a string to be passed to the command line
def get_options(run_info):
    options_str = ''
    for element in run_info:
        if element.startswith('-'):
            if type(run_info[element]) == bool:
                if run_info[element]:
                    options_str += f'{element} '
            else:
                if run_info[element] != '':
                    if ' ' in run_info[element]:
                        b = r'\"'
                        q = '"'
                        value = run_info[element].replace(' ', '_')

                        #options_str += f'{element} "{run_info[element]}" '
                        options_str += f'{element} {value} ' #\"{run_info[element]}\"
                        #options_str = str(element)+r' "'+str(run_info[element])+r'" '

                    else:
                        options_str += f'{element} {run_info[element]} '
    
    return options_str