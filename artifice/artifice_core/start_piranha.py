import docker
import os

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import update_log

def launch_piranha(run_info, font, docker_client):
    config = artifice_core.consts.retrieve_config()
    runs_dir = artifice_core.consts.RUNS_DIR
    artifice_core.start_rampart.prepare_run(run_info,runs_dir=runs_dir,font=font,output=True)

    options_str = artifice_core.start_rampart.get_options(run_info)

    run_path = runs_dir / run_info['title']
    basecalled_path = run_info['basecalledPath']
    output_path = run_info['outputPath']
    piranha_container = start_piranha(run_path, basecalled_path, output_path, docker_client, config['PIRANHA_IMAGE'], threads=config['THREADS'], container=None)

    return piranha_container

# starts a container with the piranha docker image
def start_piranha(run_path, basecalled_path, output_path, client, image, threads = artifice_core.consts.THREADS, container = None, options_str = ''):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    container_name = "piranha"

    artifice_core.start_rampart.stop_docker(client=client, container_name=container_name, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled', f'{output_path}:/data/run_data/output']
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')

    env_str = f'THREADS={threads} {options_str}'
    environment = [env_str]
    log_environment = str(environment)
    update_log(f'environment variables: {log_environment}')

    #entrypoint = f'/bin/bash source /venv/bin/activate && piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled --outdir /data/run_data/output/piranha_output -t ${threads}'
    container = client.containers.run(image=image, detach=True, name=container_name, volumes=volumes, environment=environment)


    return container
