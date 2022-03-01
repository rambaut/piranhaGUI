import docker

import artifice_core.start_rampart

#def launch_piranha(run_info, client, runs_dir = artifice_core.consts.RUNS_DIR, font = None, container = None):

def start_piranha(run_path, basecalled_path, client, image, container = None):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    containerName = "piranha"

    artifice_core.start_rampart.stop_docker(client=client,containerName=containerName, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    log_volumes = str(volumes)
    #update_log(f'volumes: {log_volumes}')

    container = client.containers.run(image=image, detach=False, name=containerName, volumes=volumes)


    return container
