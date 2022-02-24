import PySimpleGUI as sg
import os.path
import json
from webbrowser import open_new_tab
import traceback
from time import sleep

import consts
import view_barcodes_window
import start_rampart
from update_log import update_log

def launch_rampart(run_info, client, firstPort = 1100, secondPort = 1200, runs_dir = consts.RUNS_DIR, font = None, container = None):
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')
    title = run_info['title']
    update_log(f'launching RAMPART on run: "{title}"')
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')

    basecalled_path = run_info['basecalledPath']

    config_path = runs_dir+'/'+title+'/run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dump(run_configuration, file)
        #file.write(config_json)

    view_barcodes_window.check_barcodes(run_info,font=font)

    run_path = runs_dir+'/'+run_info['title']
    container = start_rampart.start_rampart(run_path, basecalled_path, client, consts.DOCKER_IMAGE, firstPort = firstPort, secondPort = secondPort, container=container)

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
        r = requests.get(f'http://localhost:{consts.RAMPART_PORT_1}')
        if r.status_code == 200:
            update_log(f'detected RAMPART running on port: {consts.RAMPART_PORT_1}')
            return True
        else:
            return False
    except:
        return False

def rampart_tab_event(event, run_info, docker_client, rampart_container, rampart_running, font):
    event = event[12:]
    print(event)

    if event == '-VIEW BARCODES-':
        try:
            view_barcodes_window.check_barcodes(run_info, font=font)

            barcodes = consts.RUNS_DIR+'/'+run_info['title']+'/barcodes.csv'
            barcodes_window, column_headers = view_barcodes_window.create_barcodes_window(barcodes,font=font)
            view_barcodes_window.run_barcodes_window(barcodes_window,barcodes,column_headers)
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    elif event == '-START/STOP RAMPART-':
        try:
            if rampart_running:
                #try:
                    #print(rampart_container.top())
                #except:
                #    pass
                rampart_running = False
                start_rampart.stop_docker(client=docker_client, container=rampart_container)
                window['-VIEW RAMPART-'].update(visible=False)
                window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                window['-RAMPART STATUS-'].update('RAMPART is not running')
            else:
                rampart_container = launch_rampart(run_info, docker_client, firstPort=consts.RAMPART_PORT_1, secondPort=consts.RAMPART_PORT_2, font=font, container=rampart_container)
                rampart_running = True
                window['-VIEW RAMPART-'].update(visible=True)
                window['-START/STOP RAMPART-'].update(text='Stop RAMPART')
                window['-RAMPART STATUS-'].update('RAMPART is running')
                #print(rampart_container.logs())

        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    elif event == '-VIEW RAMPART-':
        address = 'http://localhost:'+str(consts.RAMPART_PORT_1)
        update_log(f'opening address: "{address}" in browser to view RAMPART')
        try:
            open_new_tab(address)
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

                #print(rampart_container.logs())
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    return run_info, docker_client, rampart_container, rampart_running
