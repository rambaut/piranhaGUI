import PySimpleGUI as sg
import os.path
import json
from webbrowser import open_new_tab
import traceback

import artifice_core.consts
import artifice_core.view_barcodes_window
import artifice_core.start_rampart
from artifice_core.update_log import update_log


def rampart_tab_event(event, run_info, docker_client, rampart_container, rampart_running, font, window):
    event = event[12:]

    if event == '-VIEW BARCODES-':
        try:
            artifice_core.view_barcodes_window.check_barcodes(run_info, font=font)

            barcodes = artifice_core.consts.RUNS_DIR+'/'+run_info['title']+'/barcodes.csv'
            barcodes_window, column_headers = artifice_core.view_barcodes_window.create_barcodes_window(barcodes,font=font)
            artifice_core.view_barcodes_window.run_barcodes_window(barcodes_window,barcodes,column_headers)
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
                artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                window['-RAMPART TAB-VIEW RAMPART-'].update(visible=False)
                window['-RAMPART TAB-START/STOP RAMPART-'].update(text='Start RAMPART')
                window['-RAMPART TAB-RAMPART STATUS-'].update('RAMPART is not running')
            else:
                rampart_container = artifice_core.start_rampart.launch_rampart(run_info, docker_client, firstPort=artifice_core.consts.RAMPART_PORT_1, secondPort=artifice_core.consts.RAMPART_PORT_2, font=font, container=rampart_container)
                rampart_running = True
                window['-RAMPART TAB-VIEW RAMPART-'].update(visible=True)
                window['-RAMPART TAB-START/STOP RAMPART-'].update(text='Stop RAMPART')
                window['-RAMPART TAB-RAMPART STATUS-'].update('RAMPART is running')
                #print(rampart_container.logs())

        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    elif event == '-VIEW RAMPART-':
        address = 'http://localhost:'+str(artifice_core.consts.RAMPART_PORT_1)
        update_log(f'opening address: "{address}" in browser to view RAMPART')
        try:
            open_new_tab(address)
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    return run_info, docker_client, rampart_container, rampart_running, window
