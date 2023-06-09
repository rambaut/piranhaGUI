import PySimpleGUI as sg
import traceback
import re
import docker
import multiprocessing
import threading
import queue
import os.path
import sys
from webbrowser import open_new_tab

import artifice_core.start_rampart
import artifice_core.consts
import artifice_core.select_protocol_window
import artifice_core.piranha_options_window
from artifice_core.start_piranha import launch_piranha
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import print_container_log, check_stop_on_close, get_pre_log, setup_check_container, error_popup, translate_text, get_translate_scheme, scale_image
from artifice_core.alt_button import AltButton

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

def setup_layout(theme='Dark', font = None, version = 'ARTIFICE'):
    sg.theme(theme)
    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    is_piranhaGUI = version.startswith('piranhaGUI')

    rampart_running, rampart_button_text, rampart_status, got_rampart_image = setup_check_container('RAMPART')
    rampart_button_text = translate_text(rampart_button_text,language,translate_scheme)
    rampart_status = translate_text(rampart_status,language,translate_scheme)
    piranha_running, piranha_button_text, piranha_status, got_piranha_image = setup_check_container('Analysis')
    piranha_button_text = translate_text(piranha_button_text,language,translate_scheme)
    piranha_status = translate_text(piranha_status,language,translate_scheme)


    SHOW_RAMPART = config['SHOW_RAMPART']
    if SHOW_RAMPART == False:
        got_rampart_image = False
        rampart_running = False


    rampart_tab = [
    [sg.Multiline(size=(100,20),write_only=True, font=artifice_core.consts.CONSOLE_FONT,expand_x=True, key='-RAMPART OUTPUT-'),],
    ]

    piranha_tab = [
    [sg.Multiline(size=(100,20),write_only=True, font=artifice_core.consts.CONSOLE_FONT,expand_x=True, key='-PIRANHA OUTPUT-'),],
    ]

    button_size=(220,36)
    rampart_tab_title = translate_text('RAMPART OUTPUT',language,translate_scheme)
    piranha_tab_title = translate_text('PIRANHA OUTPUT',language,translate_scheme)
    selected_protocol_text = translate_text('Selected Protocol',language,translate_scheme) + ": " + str(config["PROTOCOL"])

    layout = [
    [AltButton(button_text=translate_text('Edit run',language,translate_scheme),size=button_size,font=font,key='-EDIT-'),],
    [sg.Text(rampart_status, visible=SHOW_RAMPART, key='-RAMPART STATUS-',),sg.Push(),
    sg.Text(selected_protocol_text, visible=got_rampart_image, key='-PROTOCOL STATUS-'),
    AltButton(button_text=translate_text('Select Another Protocol',language,translate_scheme),size=button_size,font=font, visible=got_rampart_image, key='-SELECT PROTOCOL-')],
    [
    AltButton(button_text=rampart_button_text,size=button_size, visible=got_rampart_image, font=font,key='-START/STOP RAMPART-'),
    AltButton(button_text=translate_text('Display RAMPART',language,translate_scheme),size=button_size,font=font,visible=rampart_running,key='-VIEW RAMPART-'),
    ],
    [sg.Text(piranha_status,visible=is_piranhaGUI, key='-PIRANHA STATUS-'),],
    [
    AltButton(button_text=piranha_button_text,size=button_size,font=font, visible=got_piranha_image, key='-START/STOP PIRANHA-'),
    AltButton(button_text=translate_text('Analysis Options',language,translate_scheme),size=button_size,font=font,visible=got_piranha_image,key='-PIRANHA OPTIONS-'),
    AltButton(button_text=translate_text('Open Report',language,translate_scheme),size=button_size, font=font, visible=False, key='-VIEW PIRANHA-'),
    ],
    [sg.TabGroup([[sg.Tab(rampart_tab_title,rampart_tab,visible=SHOW_RAMPART,key='-RAMPART TAB-'),sg.Tab(piranha_tab_title,piranha_tab,visible=is_piranhaGUI,key='-PIRANHA TAB-')]],expand_x=True)],
    ]


    return layout, rampart_running, piranha_running

def create_main_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating main window')
    #make_theme()
    layout, rampart_running, piranha_running = setup_layout(theme=theme, version=version, font=font)
    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))

    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window, rampart_running, piranha_running

def run_main_window(window, run_info, version = 'ARTIFICE', font = None, rampart_running = False, piranha_running = False, scale = 1):
    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    rampart_protocol = config['PROTOCOL']

    docker_client = docker.from_env()
    rampart_container = None
    rampart_log_queue = queue.Queue()
    piranha_container = None
    piranha_log_queue = queue.Queue()

    if rampart_running:
        container = get_pre_log(docker_client, rampart_log_queue, 'rampart')

    if piranha_running:
        container = get_pre_log(docker_client, piranha_log_queue, 'piranha')


    while True:
        event, values = window.read(timeout=500)

        if event != '__TIMEOUT__':
            log_event(f'{event} [main window]')


        if piranha_running:
            try:
                piranha_finished = print_container_log(piranha_log_queue, window, '-PIRANHA OUTPUT-', config['PIRANHA_LOGFILE'])
                if piranha_finished:
                    piranha_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=piranha_container)
                    window['-START/STOP PIRANHA-'].update(text=translate_text('Start Analysis',language,translate_scheme))
                    window['-PIRANHA STATUS-'].update(translate_text('Analysis is not running',language,translate_scheme))
                    window['-VIEW PIRANHA-'].update(visible=True)
                    try:
                        output_path = run_info['outputPath']
                        output_file = f'{output_path}/report.html'
                        if os.path.isfile(output_file):
                            open_new_tab(output_file)
                    except:
                        pass

            except Exception as err:
                error_popup(err, font)

        if rampart_running:
            rampart_finished = print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', config['RAMPART_LOGFILE'])
            if rampart_finished:
                rampart_running = False
                artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                window['-VIEW RAMPART-'].update(visible=False)
                window['-START/STOP RAMPART-'].update(text=translate_text('Start RAMPART',language,translate_scheme))
                window['-RAMPART STATUS-'].update(translate_text('RAMPART is not running',language,translate_scheme))

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            running_tools = []

            if rampart_running:
                running_tools.append('RAMPART')
            if piranha_running:
                running_tools.append('PIRANHA')
            try:
                check_stop_on_close(running_tools, window, docker_client, rampart_container, font=font)
            except Exception as err:
                error_popup(err, font)


            break

        elif event == '-START/STOP RAMPART-':
            try:
                if rampart_running:
                    rampart_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', config['RAMPART_LOGFILE'])
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text=translate_text('Start RAMPART',language,translate_scheme))
                    window['-RAMPART STATUS-'].update(translate_text('RAMPART is not running',language,translate_scheme))
                else:
                    art_protocol_path = config['PROTOCOLS_DIR'] / rampart_protocol
                    protocol_path = artifice_core.select_protocol_window.get_protocol_dir(art_protocol_path)
                    rampart_container = artifice_core.start_rampart.launch_rampart(
                            run_info, docker_client,
                            firstPort=config['RAMPART_PORT_1'], secondPort=config['RAMPART_PORT_2'],
                            font=font, container=rampart_container,
                            protocol_path=protocol_path
                            )
                    rampart_running = True
                    window['-VIEW RAMPART-'].update(visible=True)
                    window['-START/STOP RAMPART-'].update(text=translate_text('Stop RAMPART',language,translate_scheme))
                    window['-RAMPART STATUS-'].update(translate_text('RAMPART is running',language,translate_scheme))

                    rampart_log = rampart_container.logs(stream=True)
                    rampart_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(rampart_log, rampart_log_queue), daemon=True)
                    rampart_log_thread.start()

                    update_log('',filename=config['RAMPART_LOGFILE'],overwrite=True)

                    window['-RAMPART TAB-'].select() 

            except Exception as err:
                error_popup(err, font)

        elif event == '-START/STOP PIRANHA-':
            try:
                if piranha_running:
                    piranha_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container_name='piranha', container=piranha_container)
                    print_container_log(piranha_log_queue, window, '-PIRANHA OUTPUT-', config['PIRANHA_LOGFILE'])
                    window['-START/STOP PIRANHA-'].update(text=translate_text('Start Analysis',language,translate_scheme))
                    window['-PIRANHA STATUS-'].update(translate_text('Analysis is not running',language,translate_scheme))

                else:
                    piranha_container = launch_piranha(run_info, font, docker_client)
                    piranha_running = True
                    window['-START/STOP PIRANHA-'].update(text=translate_text('Stop Analysis',language,translate_scheme))
                    window['-PIRANHA STATUS-'].update(translate_text('Analysis is running',language,translate_scheme))

                    piranha_log = piranha_container.logs(stream=True)
                    piranha_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(piranha_log, piranha_log_queue), daemon=True)
                    piranha_log_thread.start()

                    update_log('',filename=config['PIRANHA_LOGFILE'],overwrite=True)

                    window['-PIRANHA TAB-'].select()

            except Exception as err:
                error_popup(err, font)

        elif event == '-VIEW RAMPART-':
            address = 'http://localhost:'+str(config['RAMPART_PORT_1'])
            update_log(f'opening address: "{address}" in browser to view RAMPART')

            try:
                open_new_tab(address)
            except Exception as err:
                error_popup(err, font)

        elif event == '-VIEW PIRANHA-':
            try:
                output_path = run_info['outputPath']
                """
                if sys.platform.startswith("darwin"):
                    open_new_tab(f'file:///{output_path}/piranha_output/report.html')
                else:
                    open_new_tab(f'{output_path}/piranha_output/report.html')
                """
                open_new_tab(f'file:///{output_path}/piranha_output/report.html')
            except Exception as err:
                error_popup(err, font)

        elif event == '-SELECT PROTOCOL-':
            try:
                protocol_window = artifice_core.select_protocol_window.create_protocol_window(font=font, scale=scale, version=version)
                rampart_protocol = artifice_core.select_protocol_window.run_protocol_window(protocol_window, font=font, scale=scale, version=version)
                if rampart_protocol != None:
                    window['-PROTOCOL STATUS-'].update(f'Selected Protocol: {rampart_protocol}')

            except Exception as err:
                error_popup(err, font)

        elif event == '-PIRANHA OPTIONS-':
            try:
                piranha_options_window = artifice_core.piranha_options_window.create_piranha_options_window(font=font, scale=scale, version=version)
                run_info = artifice_core.piranha_options_window.run_piranha_options_window(piranha_options_window, run_info, font=font, version=version)
  
            except Exception as err:
                error_popup(err, font)

        elif event == '-EDIT-':
            #rampart_log_queue.task_done()
            #piranha_log_queue.task_done()
            window.close()
            return True



    window.close()

if __name__ == '__main__':
    font = (artifice_core.consts.FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
