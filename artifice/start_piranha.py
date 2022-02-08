import docker

import start_rampart

def start_piranha(run_path, basecalled_path, client, image, container = None):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    containerName = "piranha"

    start_rampart.stop_docker(client=client,containerName=containerName, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')

    container = client.containers.run(image=image, detach=True, name=containerName, volumes=volumes)


    return container
