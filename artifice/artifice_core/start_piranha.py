import docker
import os
from pathlib import Path

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import update_log
from artifice_core.manage_runs import save_run

def launch_piranha(run_info, docker_client):
    config = artifice_core.consts.retrieve_config()
    runs_dir = artifice_core.consts.RUNS_DIR
    artifice_core.start_rampart.prepare_run(run_info,runs_dir=runs_dir,output=True)

    options_str = artifice_core.start_rampart.get_options(run_info)
    phylo_dir = ''
    if 'PHYLO_DIR' in run_info:
        if run_info['PHYLO_DIR'] != '':
            options_str += '-sd /data/run_data/phylo_datadir'
            phylo_dir = run_info['PHYLO_DIR']

    dirpath, iter = set_outputpath_to_runname(run_info, iter = 0)
    run_info['outputIter'] = iter
    save_run(run_info, title=run_info['title'], overwrite=True)
    print(dirpath)

    run_path = runs_dir / run_info['title']
    basecalled_path = run_info['basecalledPath']
    output_path = dirpath
    piranha_container = start_piranha(run_path, basecalled_path, output_path, docker_client, config['PIRANHA_IMAGE'],
                                       threads=config['THREADS'], container=None, options_str=options_str, phylo_dir=phylo_dir)

    return piranha_container, run_info

def set_outputpath_to_runname(run_info, iter = 0):
    if '--runname' in run_info and len(run_info['--runname']) > 0:
        dirpath = str(Path(run_info['outputPath']) / run_info['--runname'])
    else:
        dirpath = run_info['outputPath']

    if iter > 0:
        dirpath = dirpath + '('+str(iter)+')'
    if os.path.isdir(dirpath):
        dirpath, iter = set_outputpath_to_runname(run_info, iter=iter+1)
    
    return dirpath, iter

# starts a container with the piranha docker image
def start_piranha(run_path, basecalled_path, output_path, client, image, threads = artifice_core.consts.THREADS, container = None, options_str = '', phylo_dir=''):
    if client == None:
        client = docker.from_env()

    config_file = 'run_configuration.json'
    container_name = "piranha"

    artifice_core.start_rampart.stop_docker(client=client, container_name=container_name, container=container)

    volumes = [f'{run_path}:/data/run_data/analysis', f'{basecalled_path}:/data/run_data/basecalled', f'{output_path}:/data/run_data/output']
    if phylo_dir != '':
        volumes.append(f'{phylo_dir}:/data/run_data/phylo_datadir')
    log_volumes = str(volumes)
    update_log(f'volumes: {log_volumes}')

    env_str = f'THREADS={threads} {options_str}'
    environment = [env_str]
    #environment = {'THREADS':f'{threads} {options_str}'}
    log_environment = str(environment)
    update_log(f'environment variables: {log_environment}')

    #entrypoint = f'/venv/bin/activate && piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled --outdir /data/run_data/output/piranha_output -t ${threads}'
    #entrypoint = f'/venv/bin/activate'
    ##command = ['/venv/bin/activate', f'§piranha -b /data/run_data/analysis/barcodes.csv -i /data/run_data/basecalled --outdir /data/run_data/output/piranha_output -t ${threads}']

    container = client.containers.run(image=image, detach=True, name=container_name, volumes=volumes, environment=environment)


    return container
