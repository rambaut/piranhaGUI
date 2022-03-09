import docker

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import update_log

#def launch_piranha(run_info, client, runs_dir = artifice_core.consts.RUNS_DIR, font = None, container = None):
def launch_piranha(run_info, font, docker_client):
    runs_dir = artifice_core.consts.RUNS_DIR
    artifice_core.start_rampart.prepare_run(run_info,runs_dir=runs_dir,font=font,output=True)

    run_path = runs_dir+'/'+run_info['title']
    basecalled_path = run_info['basecalledPath']
    output_path = run_info['outputPath']
    piranha_container = start_piranha(run_path, basecalled_path, output_path, docker_client, artifice_core.consts.PIRANHA_IMAGE, container=None)

    return piranha_container


def start_piranha(run_path, basecalled_path, output_path, client, image, container = None):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    container_name = "piranha"

    artifice_core.start_rampart.stop_docker(client=client, container_name=container_name, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled', f'{output_path}:/data/run_data/output']
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')

    container = client.containers.run(image=image, detach=True, name=container_name, volumes=volumes)


    return container
