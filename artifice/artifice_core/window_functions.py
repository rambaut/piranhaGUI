import PySimpleGUI as sg
import queue
import threading
import traceback
import csv
import base64
import os.path
import sys
from os import mkdir
from PIL import Image
from io import BytesIO

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.alt_popup import alt_popup, alt_popup_yes_no

# prints the queued log output until it's empty, prints a message if container stopped
def print_container_log(log_queue, window, output_key, logfile,):
    queue_empty = False
    while not queue_empty:
        try:
            output = log_queue.get(block=False)
            log_queue.task_done()
            if sys.platform.startswith("darwin"): #macOS
                window[output_key].print(output, font='Menlo', end='')
            else:
                window[output_key].print(output, font='Coruier New', end='')
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
        chk_stop = alt_popup_yes_no(f'Do you wish to stop {name} while closing?', font=font)
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
    elif tool_name == 'PIRANHA' or 'Analysis':
        image_tag = artifice_core.consts.PIRANHA_IMAGE

    got_image, docker_client = artifice_core.start_rampart.check_for_image(None, image_tag, font=None, popup=False)

    if not got_image:
        status = f'{tool_name} is not installed'
        return False, '', status, got_image

    if tool_name == 'RAMPART':
        running = artifice_core.start_rampart.check_rampart_running()
    elif tool_name == 'PIRANHA' or 'Analysis':
        running = artifice_core.start_rampart.check_container('piranha')
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

    translate_scheme = get_translate_scheme()
    config = artifice_core.consts.retrieve_config()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    er_tr = translate_text('Error',language,translate_scheme)
    error_message = f'{er_tr}: {err}'

    layout = [
            [sg.Text(error_message,)],
            [AltButton(button_text=translate_text('Show logs',language,translate_scheme),font=font,key='-SHOW LOG-')],
            [sg.Multiline(log, size=(80,15), visible=False,key='-LOG-')],
            [AltButton(button_text=translate_text('OK',language,translate_scheme),font=font,key='-EXIT-')],

    ]
    #inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    error_popup = sg.Window(translate_text('ERROR',language,translate_scheme), layout, disable_close=False, finalize=True,
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

#set scaling for all window elements based on screen resolution
def scale_window(font=None):
    layout = [[sg.Text('setting up..')]]
    window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)
    resolution = window.get_screen_dimensions()[1]
    scale = resolution/1080
    update_log(f'scaling by {scale}')
    sg.set_options(scaling=scale)
    window.close()
    artifice_core.consts.edit_config('SCALING', scale)
    return scale


def scale_image(filename, scale, size, output_name = ''):
    if not os.path.isdir(artifice_core.consts.get_datadir() / 'resources'):
        mkdir(artifice_core.consts.get_datadir() / 'resources')

    processed_image = str(artifice_core.consts.get_datadir() / 'resources' / filename)
    image_file = f'./resources/{filename}'
    size = (int(size[0]*scale), int(size[1]*scale))
    im = Image.open(image_file)
    im = im.resize(size, resample=Image.BICUBIC)
    #im.save(processed_image)

    buffered = BytesIO()
    im.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue())


def get_translate_scheme(filepath = './resources/translation_scheme.csv'):
    with open(filepath, newline = '', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        scheme_list = list(csvreader)

    return scheme_list

# Takes text (in english) and returns version in given language if translation in scheme
def translate_text(string: str, language: str, scheme_list = None, append_scheme = False, vb = False):
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
            try:
                if row[lang_pos] != '':
                    return_string = row[lang_pos]
                    break
                else:
                    break
            except:
                break

    if append_scheme:
        if not string_in_scheme:
            scheme_list.append([string,])
            with open('./resources/translation_scheme.csv', 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                for row in scheme_list:
                    csvwriter.writerow(row)

    if vb: # for debugging
        print(language)
        print(return_string)

    return return_string

# Creates a layout for a window that embeds a content frame into an ARTIC header and footer
def setup_header_footer(content, large=False):
    sg.theme("HEADER")
    if large:
        layout = [
        [
            sg.Image(scale_image("artic-small.png", 1, (64,64)), pad=(8,2)),
            sg.Column([[
                sg.Text('Powered by ARTIFICE', font=('Helvetica Neue Light', 14), pad=(8,2)),],[
                sg.Text('ARTICnetwork: http://artic.network', font=('Helvetica Neue Light', 24), pad=(8,2))
            ]],)
        ],
        [
            content
        ],
        [
            sg.Text('ARTIFICE developed by Corey Ansley, Áine O\'Toole, Rachel Colquhoun, Zoe Vance & Andrew Rambaut', font=('Helvetica Neue Light', 12), pad=(8,2)),
            sg.Text('Wellcome Trust Award 206298/Z/17/Z', font=('Helvetica Neue Light', 12), pad=(8,2), expand_x=True, justification='right'),
        ]]
    else:
        layout = [
        [
            sg.Image(scale_image("artic-small.png", 1, (32,32)), pad=(8,2)),
            sg.Text('Powered by ARTIFICE | ARTICnetwork: http://artic.network', font=('Helvetica Neue Light', 14), pad=(8,2)),
        ],
        [
            content
        ],
        [
            sg.Text('Wellcome Trust Award 206298/Z/17/Z', font=('Helvetica Neue Light', 12), pad=(8,2)),
        ]]

    return layout

# Creates a frame that embeds a content panel in a Piranha/PoSeqCo branded layout
def setup_content(panel, translator, button_text=None, button_key=None):
    sg.theme("CONTENT")

    layout = [
        [ 
            sg.Column(
                [[sg.Image(scale_image("piranha.png", 1, (64,64)))]],
                pad=(8,0)
            ),
            sg.Column(
                [
                    [sg.Text("Piranha v1.4.3", font=('Helvetica Neue Thin', 32))],
                    [sg.Text("Polio Direct Detection by Nanopore Sequencing (DDNS)", font=('Helvetica Neue Light', 12))],
                    [sg.Text("analysis pipeline and reporting tool", font=('Helvetica Neue Light', 12))],             
                ]
            ),
            sg.Column(
                [[sg.Image(scale_image("poseqco_logo_cropped.png", 1, (150,68)))],
                [sg.Text("Bill & Melinda Gates Foundation OPP1171890 and OPP1207299", font=('Helvetica Neue Light', 12))]],
                element_justification="right", expand_x=True, pad=(8,0))
        ],
        # [sg.HorizontalSeparator()],
        [
            panel,
        ],
        # [sg.HorizontalSeparator()],
    ]
    if button_text != None:
        layout.append(
            [sg.Push(), AltButton(button_text=translator(button_text),key=button_key)]
            )

    return sg.Frame("", [[sg.Column(layout, pad=(0, 0))]], expand_x=True, border_width=0)

