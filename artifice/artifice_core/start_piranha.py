import docker

import artifice_core.start_rampart
import artifice_core.consts

#def launch_piranha(run_info, client, runs_dir = artifice_core.consts.RUNS_DIR, font = None, container = None):
def launch_piranha(run_info, font, docker_client):
    runs_dir = artifice_core.consts.RUNS_DIR
    artifice_core.start_rampart.prepare_run(run_info,runs_dir=runs_dir,font=font)

    run_path = runs_dir+'/'+run_info['title']
    basecalled_path = run_info['basecalledPath']
    piranha_container = start_piranha(run_path, basecalled_path, docker_client, artifice_core.consts.PIRANHA_IMAGE, container=None)

    return piranha_container


def start_piranha(run_path, basecalled_path, client, image, container = None):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    containerName = "piranha"

    artifice_core.start_rampart.stop_docker(client=client, containerName=containerName, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled']
    log_volumes = str(volumes)
    print(log_volumes)
    #update_log(f'volumes: {log_volumes}')

    container = client.containers.run(image=image, detach=True, name=containerName, volumes=volumes)


    return container
