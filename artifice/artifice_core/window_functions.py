import PySimpleGUI as sg
import queue
import threading
import traceback
import csv

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton

# prints the queued log output until it's empty, prints a message if container stopped
def print_container_log(log_queue, window, output_key, logfile):
    queue_empty = False
    while not queue_empty:
        try:
            output = log_queue.get(block=False)
            log_queue.task_done()
            window[output_key].print(output, end='')
            update_log(output, filename=logfile, add_newline=False)
            if output == '###CONTAINER STOPPED###\n':
                return True
        except queue.Empty:
            queue_empty = True
            pass

    return False

# asks the user whether they would like to stop the running container(s) when they close the window
def check_stop_on_close(names: list, window, client, container, font = None):
    to_stop = []
    for name in names:
        chk_stop = sg.popup_yes_no(f'Do you wish to stop {name} while closing?', font=font)
        if chk_stop == 'Yes':
            to_stop.append(name)
        else:
            update_log(f'User chose to keep {name} running')

    window.close()

    for name in to_stop:
        container_name = name.lower()
        update_log(f'stopping {name}...')
        artifice_core.start_rampart.stop_docker(client=client, container=None, container_name=container_name)
        update_log(f'{name} stopped')

# queues the log output from already running container
def get_pre_log(client, log_queue, container_name):
    container = client.containers.get(container_name)
    log = container.logs(stream=True)
    log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(log, log_queue), daemon=True)
    log_thread.start()

    return container

# checks if container running
def setup_check_container(tool_name):
    update_log(f'checking if {tool_name} is running...')
    running = False
    if tool_name == 'RAMPART':
        image_tag = artifice_core.consts.RAMPART_IMAGE
    elif tool_name == 'PIRANHA':
        image_tag = artifice_core.consts.PIRANHA_IMAGE

    got_image, docker_client = artifice_core.start_rampart.check_for_image(None, image_tag, font=None, popup=False)

    if not got_image:
        status = f'{tool_name} is not installed'
        return False, '', status, got_image

    if tool_name == 'RAMPART':
        running = artifice_core.start_rampart.check_rampart_running()
    else:
        container_name = tool_name.lower()
        running = artifice_core.start_rampart.check_container(container_name)

    if running:
        button_text = f'Stop {tool_name}'
        status = f'{tool_name} is running'
    else:
        button_text = f'Start {tool_name}'
        status = f'{tool_name} is not running'

    return running, button_text, status, True

# creates a popup stating the exception raised with option of showing the logs
def error_popup(err, font):
    update_log(traceback.format_exc())
    sg.theme('Artifice')
    #log = ''
    filepath = str(artifice_core.consts.get_datadir() / artifice_core.consts.LOGFILE)
    with open(filepath, 'r') as logfile:
        log = logfile.read()

    layout = [
            [sg.Text(f'Error: {err}',)],
            [AltButton(button_text='Show logs',font=font,key='-SHOW LOG-')],
            [sg.Multiline(log, size=(80,15), visible=False,key='-LOG-')],
            [AltButton(button_text='OK',font=font,key='-EXIT-')],

    ]
    #inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    error_popup = sg.Window('ERROR', layout, disable_close=False, finalize=True,
                                font=font, resizable=False, no_titlebar=False,)
    AltButton.intialise_buttons(error_popup)

    run_error_popup(error_popup)
    #sg.popup_error(AltButton(button_text='Launch ARTIFICE',font=('Arial',18),key='-LAUNCH-'))

def run_error_popup(window):
    while True:
        #config = artifice_core.consts.retrieve_config()
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED or event == '-EXIT-':
            window.close()
            break
            return
        elif event == '-SHOW LOG-':
            window['-LOG-'].update(visible=True)
            window['-SHOW LOG-'].update(visible=False)


    window.close()
    return None

def get_translate_scheme(filepath = './resources/translation_scheme.csv'):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        scheme_list = list(csvreader)

    return scheme_list

# Takes text (in english) and returns version in given language if translation in scheme
def translate_text(string: str, language: str, scheme_list = None, append_scheme = True):
    if scheme_list == None or append_scheme:
        scheme_list = get_translate_scheme()

    languages = scheme_list[0]
    lang_pos = 0
    for lang in languages:
        if lang == language:
            lang_pos = languages.index(language)

    return_string = string # if no translation exists, the given string is returned back
    string_in_scheme = False
    for row in scheme_list:
        if string == row[0]:
            string_in_scheme = True
            if row[lang_pos] != '':
                return_string = row[lang_pos]
                break

    if append_scheme:
        if not string_in_scheme:
            scheme_list.append([string,])
            with open('./resources/translation_scheme.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                for row in scheme_list:
                    csvwriter.writerow(row)


    return return_string
