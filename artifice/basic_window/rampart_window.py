import subprocess
import PySimpleGUI as sg
import traceback
import re
import docker
import multiprocessing
from os import cpu_count
import threading
import queue
import os.path
import sys
from webbrowser import open_new_tab
import webbrowser

from artifice_core.language import translator
import artifice_core.start_rampart
import artifice_core.consts as consts
import artifice_core.select_protocol_window
import artifice_core.piranha_options_window
import artifice_core.window_functions as window_functions
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import print_container_log, check_stop_on_close, get_pre_log, setup_check_container, error_popup
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse

def setup_panel(config):
    sg.theme("PANEL")

    theme = consts.THEMES[sg.theme()]

    is_piranhaGUI = True

    rampart_running, rampart_button_text, rampart_status, got_rampart_image = setup_check_container('RAMPART')
    rampart_button_text = translator(rampart_button_text)
    rampart_status = translator(rampart_status)

    y1 = 24
    y2 = 48

    column1 = [
            [
                sg.Sizer(1,y1),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Samples:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y1),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('MinKnow run:'), pad=(0,12), expand_y=True),
            ]]
    column2 = [
            [                
                sg.Sizer(1,y1),
                sg.Text(translator('Select a CSV file containing the IDs and barcodes for each sample:'),font=consts.CAPTION_FONT),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-SAMPLES-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-SAMPLES-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFileBrowse(button_text=translator('Select'),file_types=(("CSV Files", "*.csv"),)),
                AltButton(button_text=translator('View'),key='-VIEW SAMPLES-'),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [                
                sg.Sizer(1,y1),
                sg.Text(translator('Select the folder containing sequencing reads from MinKnow:'),font=consts.CAPTION_FONT),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-MINKNOW-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-MINKNOW-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select')),
                sg.Sizer(consts.BUTTON_SIZE[0], 0),
            ],
            [                
                sg.Sizer(1,16),
            ]]


    #button_size=(220,36)
    rampart_tab_title = translator('RAMPART output')
    selected_protocol_text = translator('Selected Protocol') + ": " + str(config["PROTOCOL"])

    rampart_tab = [[
        sg.Column([
            [sg.Sizer(2,2)],
            [
                sg.Multiline(write_only=True, font=consts.CONSOLE_FONT, 
                            background_color = theme['CONSOLE_BACKGROUND'], 
                            text_color=theme['CONSOLE_TEXT'],
                            expand_x=True, expand_y=True, key='-RAMPART OUTPUT-')
            ]
        ], expand_x=True, expand_y=True, pad=(2,2), background_color = theme['BUTTON'][1])
    ]]

    output_tabs = []
    output_tabs.insert(0, sg.Tab(rampart_tab_title,rampart_tab,
                                    background_color = theme['BUTTON'][1],
                                    visible=False,key='-RAMPART TAB-'))

    threads_list = [i for i in range(1, cpu_count()+1)]

    layout = []
    layout.append([
        sg.Sizer(16,16),
        sg.Frame(translator("Sequencing Run:"), [
            [
                sg.Sizer(32,0),
                sg.Column(column1, element_justification='Right'),
                sg.Column(column2, expand_x=True),      
            ]], border_width=0, relief="solid", pad=(16,8), expand_x=True, expand_y=True)
    ])
    layout.append([
        sg.Text(rampart_status, key='-RAMPART STATUS-',),sg.Push(),
        sg.Text(selected_protocol_text, visible=got_rampart_image, key='-PROTOCOL STATUS-'),
        AltButton(button_text=translator('Select Protocol'), visible=got_rampart_image, key='-SELECT PROTOCOL-')
    ])
    layout.append([
        AltButton(button_text=rampart_button_text, visible=got_rampart_image,key='-START/STOP RAMPART-'),
        AltButton(button_text=translator('Display RAMPART'),visible=rampart_running,key='-VIEW RAMPART-'),
    ])
    layout.append([sg.Sizer(16,16)])
    layout.append([sg.HorizontalSeparator()])
        
    layout.append([sg.TabGroup([output_tabs], 
                               title_color=theme['BUTTON_HOVER'][0], tab_background_color = theme['BUTTON_HOVER'][1],
                               selected_title_color=theme['BUTTON'][0], selected_background_color = theme['BUTTON'][1],
                               expand_x=True, expand_y=True)])
    
    panel = sg.Frame("",  
                     [[ sg.Column(layout, expand_x=True, expand_y=True, pad=(16,8)) ]], border_width=0, relief="solid", 
                     pad=(0,8), expand_x=True, expand_y=True)

    return panel, rampart_running

def create_main_window(window = None):
    update_log('creating main window')

    config = consts.retrieve_config()
  
    panel, rampart_running = setup_panel(config)

    title = f'RAMPART{" v" + consts.RAMPART_VERSION if consts.RAMPART_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title)

    layout = window_functions.setup_header_footer(content)


    new_window = sg.Window(title, layout, resizable=True, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT,icon=consts.ICON, margins=(0,0), element_padding=(0,0),
                           relative_location=(0,-200))
    #new_window.TKroot.minsize(1024,640)
    #new_window.TKroot.minsize(640,480)
    new_window.set_min_size(size=(800,800))
    new_window.set_title(consts.VERSION)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window, rampart_running

def run_main_window(window, rampart_running = False, piranha_running = False):
    config = consts.retrieve_config()

    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'
    docker_client = docker.from_env()

    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath'}
    try:
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], 
                            update_archive_button=False)
    except:
        pass

    rampart_protocol = config['PROTOCOL']

    docker_client = docker.from_env()
    rampart_container = None
    rampart_log_queue = queue.Queue()

    if rampart_running:
        container = get_pre_log(docker_client, rampart_log_queue, 'rampart')

    while True:
        event, values = window.read(timeout=500)

        if event != '__TIMEOUT__':
            log_event(f'{event} [main window]')

        if rampart_running:
            rampart_finished = print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', config['RAMPART_LOGFILE'])
            if rampart_finished:
                rampart_running = False
                artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                window['-VIEW RAMPART-'].update(visible=False)
                window['-START/STOP RAMPART-'].update(text=translator('Start RAMPART'))
                window['-RAMPART STATUS-'].update(translator('RAMPART is not running'))

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            running_tools = []

            if rampart_running:
                running_tools.append('RAMPART')

            try:
                check_stop_on_close(running_tools, window, docker_client, rampart_container)
            except Exception as err:
                error_popup(err)


            break

        elif event == '-VIEW SAMPLES-':
            try:
                if '-SAMPLES-' not in values:
                    error_popup("Samples not found in values")

                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-')
                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                error_popup(err)

        elif event == '-START/STOP RAMPART-':
            try:
                if rampart_running:
                    rampart_running = False
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    print_container_log(rampart_log_queue, window, '-RAMPART OUTPUT-', config['RAMPART_LOGFILE'])
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text=translator('Start RAMPART'))
                    window['-RAMPART STATUS-'].update(translator('RAMPART is not running'))
                else:
                    art_protocol_path = config['PROTOCOLS_DIR'] / rampart_protocol
                    protocol_path = artifice_core.select_protocol_window.get_protocol_dir(art_protocol_path)
                    rampart_container = artifice_core.start_rampart.launch_rampart(
                            run_info, docker_client,
                            firstPort=config['RAMPART_PORT_1'], secondPort=config['RAMPART_PORT_2'],
                            container=rampart_container,
                            protocol_path=protocol_path
                            )
                    rampart_running = True
                    window['-VIEW RAMPART-'].update(visible=True)
                    window['-START/STOP RAMPART-'].update(text=translator('Stop RAMPART'))
                    window['-RAMPART STATUS-'].update(translator('RAMPART is running'))

                    rampart_log = rampart_container.logs(stream=True)
                    rampart_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(rampart_log, rampart_log_queue), daemon=True)
                    rampart_log_thread.start()

                    update_log('',filename=config['RAMPART_LOGFILE'],overwrite=True)

                    window['-RAMPART TAB-'].select() 

            except Exception as err:
                error_popup(err)

        elif event == '-VIEW RAMPART-':
            address = 'http://localhost:'+str(config['RAMPART_PORT_1'])
            update_log(f'opening address: "{address}" in browser to view RAMPART')

            try:
                open_new_tab(address)
            except Exception as err:
                error_popup(err)

        elif event == '-SELECT PROTOCOL-':
            try:
                protocol_window = artifice_core.select_protocol_window.create_protocol_window()
                rampart_protocol = artifice_core.select_protocol_window.run_protocol_window(protocol_window)
                if rampart_protocol != None:
                    window['-PROTOCOL STATUS-'].update(f'Selected Protocol: {rampart_protocol}')

            except Exception as err:
                error_popup(err)

        elif event == '-EDIT-':
            #rampart_log_queue.task_done()
            window.close()
            return True



    window.close()

if __name__ == '__main__':
    window, rampart_running = create_main_window()
    run_main_window(window, rampart_running=rampart_running)

    window.close()
