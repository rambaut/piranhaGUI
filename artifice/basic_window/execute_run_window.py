import PySimpleGUI as sg
import traceback
import re
import docker
import multiprocessing
import threading
import queue
from webbrowser import open_new_tab

import artifice_core.start_rampart
from artifice_core.start_piranha import launch_piranha
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import print_container_log, check_stop_on_close, get_pre_log, setup_check_container

def make_theme():
    Artifice_Theme = {'BACKGROUND': "#072429",
               'TEXT': '#f7eacd',
               'INPUT': '#1e5b67',
               'TEXT_INPUT': '#f7eacd',
               'SCROLL': '#707070',
               'BUTTON': ('#f7eacd', '#d97168'),
               'PROGRESS': ('#000000', '#000000'),
               'BORDER': 1,
               'SLIDER_DEPTH': 0,
               'PROGRESS_DEPTH': 0}

    sg.theme_add_new('Artifice', Artifice_Theme)

def setup_layout(theme='Dark', font = None):
    sg.theme(theme)

    rampart_running, rampart_button_text, rampart_status = setup_check_container('RAMPART')
    piranha_running, piranha_button_text, piranha_status = setup_check_container('PIRANHA')

    rampart_tab = [
    [sg.Multiline(size=(100,20),write_only=True, key='-RAMPART OUTPUT-'),],
    ]

    piranha_tab = [
    [sg.Multiline(size=(100,20),write_only=True, key='-PIRANHA OUTPUT-'),],
    ]

    layout = [
    [sg.Button(button_text='Edit run',key='-EDIT-'),],
    [sg.Text(rampart_status, key='-RAMPART STATUS-'),],
    [
    sg.Button(button_text=rampart_button_text,key='-START/STOP RAMPART-'),
    sg.Button(button_text='Display RAMPART', visible=rampart_running,key='-VIEW RAMPART-'),
    ],
    [sg.Text(piranha_status, key='-PIRANHA STATUS-'),],
    [
    sg.Button(button_text=piranha_button_text, key='-START/STOP PIRANHA-'),
    sg.Button(button_text='Display PIRANHA', visible=False, key='-VIEW PIRANHA-'),
    ],
    [sg.TabGroup([[sg.Tab('RAMPART OUTPUT',rampart_tab,key='-RAMPART TAB-'),sg.Tab('PIRANHA OUTPUT',piranha_tab,key='-PIRANHA TAB-')]])],
    ]


    return layout, rampart_running

def create_main_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    make_theme()
    layout, rampart_running = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    return new_window, rampart_running

def run_main_window(window, run_info, font = None, rampart_running = False):
    selected_run_title = 'TEMP_RUN'

    docker_client = docker.from_env()
    rampart_container = None
    rampart_log_queue = queue.Queue()
    piranha_container = None
    piranha_running = False
    piranha_log_queue = queue.Queue()


    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath',
                    '-OUTDIR-':'outputPath'}

    if rampart_running:
        container = get_pre_log(docker_client, rampart_log_queue, 'rampart')

    if piranha_running:
        container = get_pre_log(docker_client, rampart_log_queue, 'piranha')

    while True:
        event, values = window.read(timeout=500)

        if event != '__TIMEOUT__':
            log_event(f'{event} [main window]')


        if piranha_running:
            try:
                piranha_finished = print_container_log(piranha_log_queue, window, '-PIRANHA OUTPUT-', artifice_core.consts.PIRANHA_LOGFILE)
                if piranha_finished:
                    piranha_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=piranha_container)
                    window['-START/STOP PIRANHA-'].update(text='Start PIRANHA')
                    window['-PIRANHA STATUS-'].update('PIRANHA is not running')
                    window['-VIEW PIRANHA-'].update(visible=True)
                    try:
                        output_path = run_info['outputPath']
                        open_new_tab(f'{output_path}/report.html')
                    except:
                        pass

            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        if rampart_running:
            rampart_finished = print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', artifice_core.consts.RAMPART_LOGFILE)
            if rampart_finished:
                rampart_running = False
                artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                window['-VIEW RAMPART-'].update(visible=False)
                window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                window['-RAMPART STATUS-'].update('RAMPART is not running')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            running_tools = []
            if rampart_running:
                running_tools.append('RAMPART')
            if piranha_running:
                running_tools.append('PIRANHA')

            check_stop_on_close(running_tools, window, docker_client, rampart_container, font=font)

            break

        elif event == '-START/STOP RAMPART-':
            try:
                if rampart_running:
                    rampart_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', artifice_core.consts.RAMPART_LOGFILE)
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is not running')
                else:
                    rampart_container = artifice_core.start_rampart.launch_rampart(
                            run_info, docker_client,
                            firstPort=artifice_core.consts.RAMPART_PORT_1, secondPort=artifice_core.consts.RAMPART_PORT_2,
                            font=font, container=rampart_container
                            )
                    rampart_running = True
                    window['-VIEW RAMPART-'].update(visible=True)
                    window['-START/STOP RAMPART-'].update(text='Stop RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is running')

                    rampart_log = rampart_container.logs(stream=True)
                    rampart_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(rampart_log, rampart_log_queue), daemon=True)
                    rampart_log_thread.start()

                    update_log('',filename=artifice_core.consts.RAMPART_LOGFILE,overwrite=True)

            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-START/STOP PIRANHA-':
            try:
                if piranha_running:
                    piranha_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container_name='piranha', container=piranha_container)
                    print_container_log(piranha_log_queue, window, '-PIRANHA OUTPUT-', artifice_core.consts.PIRANHA_LOGFILE)
                    window['-START/STOP PIRANHA-'].update(text='Start PIRANHA')
                    window['-PIRANHA STATUS-'].update('PIRANHA is not running')

                else:
                    piranha_container = launch_piranha(run_info, font, docker_client)
                    piranha_running = True
                    window['-START/STOP PIRANHA-'].update(text='Stop PIRANHA')
                    window['-PIRANHA STATUS-'].update('PIRANHA is running')

                    piranha_log = piranha_container.logs(stream=True)
                    piranha_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(piranha_log, piranha_log_queue), daemon=True)
                    piranha_log_thread.start()

                    update_log('',filename=artifice_core.consts.PIRANHA_LOGFILE,overwrite=True)

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

        elif event == '-VIEW PIRANHA-':
            try:
                output_path = run_info['outputPath']
                open_new_tab(f'{output_path}/report.html')
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-EDIT-':
            window.close()
            return True



    window.close()


if __name__ == '__main__':
    font = (artifice_core.consts.FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
