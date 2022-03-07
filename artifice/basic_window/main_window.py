import PySimpleGUI as sg
import traceback
import re
from datetime import datetime
from datetime import timedelta
from time import sleep, time
import multiprocessing
import threading
import queue

import artifice_core.start_rampart
import artifice_core.parse_columns_window
from artifice_core.start_piranha import launch_piranha
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_changes, load_run

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

    update_log('checking if RAMPART is running...')
    rampart_running = artifice_core.start_rampart.check_rampart_running()
    if rampart_running:
        rampart_button_text = 'Stop RAMPART'
        rampart_status = 'RAMPART is running'
    else:
        rampart_button_text = 'Start RAMPART'
        rampart_status = 'RAMPART is not running'

    layout = [
    [
    sg.Text('Samples:',size=(13,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
    sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
    sg.Button(button_text='View',key='-VIEW SAMPLES-'),
    ],
    [
    sg.Text('MinKnow run:',size=(13,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
    sg.FolderBrowse(),
    ],
    [sg.Text(rampart_status, key='-RAMPART STATUS-'),],
    [
    sg.Button(button_text=rampart_button_text,key='-START/STOP RAMPART-'),
    sg.Button(button_text='View RAMPART', visible=rampart_running,key='-VIEW RAMPART-'),
    ],
    [sg.Button(button_text='Start PIRANHA',key='-START PIRANHA-'),],
    [sg.Multiline(size=(100,20),write_only=True, key='-PIRANHA OUTPUT-'),],
    ]

    return layout, rampart_running

def create_main_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    make_theme()
    layout, rampart_running = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")

    return new_window, rampart_running

def run_main_window(window, font = None, rampart_running = False):
    print(datetime.now())
    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'
    docker_client = None
    rampart_container = None

    piranha_container = None
    piranha_running = False
    piranha_log_queue = queue.Queue()
    piranha_log_thread = None

    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath'}
    try:
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = artifice_core.consts.RUNS_DIR, update_archive_button=False)
    except:
        pass

    while True:
        event, values = window.read(timeout=500)

        if event != '__TIMEOUT__':
            log_event(f'{event} [main window]')


        if piranha_running:
            queue_empty = False
            while not queue_empty:
                try:
                    piranha_output = piranha_log_queue.get(block=False)
                    piranha_log_queue.task_done()
                    window['-PIRANHA OUTPUT-'].print(piranha_output, end='')
                except queue.Empty:
                    queue_empty = True
                    pass

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if rampart_running:
                chk_stop = sg.popup_yes_no('Do you wish to stop RAMPART while closing', font=font)
                window.close()

                if chk_stop == 'Yes':
                    update_log('stopping RAMPART...')
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    update_log('RAMPART stopped')
                else:
                    update_log('User chose to keep RAMPART running')
            break

        elif event == '-VIEW SAMPLES-':
            try:
                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-', font)
                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True, element_dict=element_dict)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event in {'-SAMPLES-FocusOut','-MINKNOW-FocusOut'}:
            try:
                if 'title' in run_info:
                    run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                else:
                    clear_selected_run(window)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)
                try:
                    run_info = load_run(window, run_info['title'])
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
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is not running')
                else:
                    run_info = save_changes(values, run_info, window, element_dict = element_dict, update_list=False)
                    rampart_container = artifice_core.start_rampart.launch_rampart(
                            run_info, docker_client,
                            firstPort=artifice_core.consts.RAMPART_PORT_1, secondPort=artifice_core.consts.RAMPART_PORT_2,
                            font=font, container=rampart_container
                            )
                    rampart_running = True
                    window['-VIEW RAMPART-'].update(visible=True)
                    window['-START/STOP RAMPART-'].update(text='Stop RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is running')
                    #print(rampart_container.logs())

            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-START PIRANHA-':
            try:
                piranha_container = launch_piranha(run_info, font, docker_client)
                piranha_log = piranha_container.logs(stream=True)
                piranha_log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(piranha_log, piranha_log_queue), daemon=True)
                piranha_log_thread.start()
                piranha_running = True

            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)


    window.close()


if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (artifice_core.consts.FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
