import PySimpleGUI as sg
import queue
import threading
import traceback
import base64
import os.path
import csv
from os import mkdir
from PIL import Image
from io import BytesIO

import artifice_core.start_rampart
import artifice_core.consts as consts
from artifice_core.language import translator
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
            window[output_key].print(output, font=consts.CONSOLE_FONT, end='')
            update_log(output, filename=logfile, add_newline=False)
            if output == '###CONTAINER STOPPED###\n':
                return True
        except queue.Empty:
            queue_empty = True
            pass

    return False

# asks the user whether they would like to stop the running container(s) when they close the window
def check_stop_on_close(names: list, window, client, container):
    to_stop = []
    for name in names:
        chk_stop = alt_popup_yes_no(f'Do you wish to stop {name} while closing?')
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

    got_image, docker_client = artifice_core.start_rampart.check_for_image(None, image_tag, popup=False)

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
def error_popup(err, information=None):

    if isinstance(err, Exception):
        message = err.args[0]
        information = err.args[1] if len(err.args) > 1 else None
    else:
        message = err

    update_log(traceback.format_exc())
    sg.theme('DEFAULT')
    #log = ''
    filepath = str(artifice_core.consts.get_datadir() / artifice_core.consts.LOGFILE)
    with open(filepath, 'r') as logfile:
        log = logfile.read()

    error_message = f'{translator("Error")}: {translator(message)}'

    information_message = translator(information) if information != None \
        else translator('Please check the log file for more information')
    
    layout = [
            [sg.Text(error_message,font=consts.SUBTITLE_FONT)],
            [sg.Text(information_message,font=consts.DEFAULT_FONT)],
            [sg.Push(),AltButton(button_text=translator('Show log file...'),font=consts.BUTTON_FONT,
                                 visible=True,key='-SHOW LOG-')],
            [sg.Multiline(log, size=(80,15), autoscroll=True, disabled=True, visible=False,key='-LOG-')],
            [sg.Push(),AltButton(button_text=translator('Hide log file'),font=consts.BUTTON_FONT,
                                 visible=False,key='-HIDE LOG-')],
            [sg.Sizer(16,16)],
            [sg.Push(),AltButton(button_text=translator('OK'),font=consts.BUTTON_FONT,key='-EXIT-'),sg.Push()],

    ]
    #inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    error_popup = sg.Window(translator('ERROR'), layout, disable_close=False, finalize=True,
                           modal=True, keep_on_top=True,
                                resizable=False, no_titlebar=False,margins=(16,16))
    AltButton.intialise_buttons(error_popup)

    run_error_popup(error_popup)

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
            # window['-HIDE LOG-'].update(visible=True)
        # elif event == '-HIDE LOG-':
        #     window['-LOG-'].update(visible=False)
        #     window['-SHOW LOG-'].update(visible=True)
        #     window['-HIDE LOG-'].update(visible=False)
        else:     
            window.close()
    return None

#set scaling for all window elements based on screen resolution
def scale_window():
    screen = sg.Window.get_screen_size()
    resolution = screen[1]
    scale = resolution/1024
    update_log(f'scaling by {scale}')
    sg.set_options(scaling=scale)
    consts.edit_config('SCALING', scale)
    return scale

def scale_image(filename, scale, size):
    if not os.path.isdir(consts.get_datadir() / 'resources'):
        mkdir(consts.get_datadir() / 'resources')

    #processed_image = str(consts.get_datadir() / 'resources' / filename)
    image_file = f'./resources/{filename}'
    image_file = consts.get_resource(image_file)
    size = (int(size[0]*scale), int(size[1]*scale))
    im = Image.open(image_file)
    im = im.resize(size, resample=Image.BICUBIC)
    #im.save(processed_image)

    buffered = BytesIO()
    im.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue())

# Creates a layout for a window that embeds a content frame into an ARTIC header and footer
def setup_header_footer(content, large=False, small=False):
    sg.theme("HEADER")
    if large:
        layout = [
        [
            sg.Image(scale_image("artic-small.png", consts.SCALING, (64,64)), pad=(8,2), 
                     enable_events=True, key='-ARTIC LOGO-'),
            sg.Column([[
                    sg.Text('Powered by ARTIFICE', font=consts.HEADER_TITLE_FONT, pad=(8,2)),
                ],[
                    sg.Text('ARTICnetwork: http://artic.network', font=consts.HEADER_FONT, pad=(8,2), 
                            enable_events=True, key='-ARTIC LOGO-')
                ]],)
        ],
        [
            content
        ],
        [
            sg.Text(consts.APPLICATION_CREDITS, font=consts.FOOTER_FONT, pad=(8,2)),
            sg.Text(consts.APPLICATION_FOOTER, font=consts.FOOTER_FONT, pad=(8,2), expand_x=True, justification='right'),
        ]]
    elif small:
        layout = [
        [
            sg.Sizer(16,16),
            # sg.Image(scale_image("artic-small.png", 1, (16,16)), pad=(8,0)),
            # sg.Push(),
            # sg.Text('ARTICnetwork: http://artic.network', font=('Helvetica Neue Light', 14), pad=(8,2)),
        ],
        [
            content
        ],
        [
            sg.Sizer(16,16)
        ]]
    else:
        layout = [
        [
            sg.Image(scale_image("artic-icon.png", 1, (32,32)), pad=(8,2), 
                     enable_events=True, key='-ARTIC LOGO-'),
            sg.Text(consts.APPLICATION_HEADER, font=consts.HEADER_FONT, 
                    pad=(8,2),enable_events=True, key='-ARTIC LOGO-'),
        ],
        [
            content
        ],
        [
            sg.Text(consts.APPLICATION_FOOTER, font=consts.FOOTER_FONT, pad=(8,2)),
        ]]

    return layout

# Creates a frame that embeds a content panel in a Application branded layout
def setup_content(panel, title=None, small=False, button_text=None, button_key=None, 
                  top_left_button_text=None, top_left_button_key=None, 
                  top_right_button_text=None, top_right_button_key=None,
                  bottom_left_button_text=None, bottom_left_button_key=None):
    sg.theme("CONTENT")

    layout = []
    if small:
        layout.append([
                sg.Sizer(16,40),
                sg.Image(scale_image(consts.ICON_FILENAME, 1, (32,32)), enable_events=True, key='-APPLICATION LOGO-'),
                sg.Sizer(16,40),
                sg.Text(title, font=('Helvetica Neue Thin', 18))
            ])
    else:
        layout.append([
                sg.Sizer(16,72),
                sg.Column(
                    [[sg.Image(scale_image(consts.ICON_FILENAME, consts.SCALING, (64,64)),
                               enable_events=True, key='-APPLICATION LOGO-')]],
                ),
                sg.Sizer(16,72),
                sg.Column(
                    [
                        [sg.Text(title, font=consts.TITLE_FONT)],
                        [sg.Text(consts.APPLICATION_TITLE_LINE_1, font=consts.SUBTITLE_FONT)],
                        [sg.Text(consts.APPLICATION_TITLE_LINE_2 , font=consts.SUBTITLE_FONT)],
                    ]
                ),
                sg.Sizer(16,72),
                sg.Column(
                    [[sg.Image(scale_image(consts.PROJECT_LOGO, 1, (150,68)),
                               enable_events=True, key='-PROJECT LOGO-')],
                    [sg.Text(consts.PROJECT_FOOTER, font=consts.FOOTER_FONT)]],
                    element_justification="right", expand_x=True, pad=(8,0))
            ])

    top_buttons = []
    top_buttons.append(sg.Sizer(16,4))
    if top_left_button_text != None:
        top_buttons.append(AltButton(button_text=translator(top_left_button_text),key=top_left_button_key))

    if top_right_button_text != None:
        top_buttons.append(sg.Push())
        top_buttons.append(AltButton(button_text=translator(top_right_button_text),key=top_right_button_key))

    top_buttons.append(sg.Sizer(16,4))

    layout.append(top_buttons)

    layout.append([panel])

    bottom_buttons = []

    bottom_buttons.append(sg.Sizer(16,4))

    if bottom_left_button_text != None:
        bottom_buttons.append(AltButton(button_text=translator(bottom_left_button_text),key=bottom_left_button_key))

    if button_text != None:
        bottom_buttons.append(sg.Push())
        bottom_buttons.append(AltButton(button_text=translator(button_text),key=button_key))

    bottom_buttons.append(sg.Sizer(16,4))

    layout.append(bottom_buttons)

    return sg.Frame("", layout, expand_x=True, expand_y=True, border_width=0)

