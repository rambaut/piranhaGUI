import PySimpleGUI as sg
import traceback
from webbrowser import open_new_tab

import artifice_core.start_rampart
from artifice_core.update_log import log_event, update_log

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

    docker_installed = artifice_core.start_rampart.check_for_docker()
    if docker_installed:
        docker_status = 'Docker installed'
        docker_text_color = None#'#00bd00' #green
    else:
        docker_status = 'Docker not installed'
        docker_text_color = '#db4325' #red

    got_rampart_image, docker_client = artifice_core.start_rampart.check_for_image(None, artifice_core.consts.RAMPART_IMAGE, font=font, popup=False)

    if got_rampart_image:
        rampart_image_status = 'RAMPART image installed'
        rampart_text_color = None
    else:
        rampart_image_status = 'RAMPART image not installed'
        rampart_text_color = '#db4325' #red

    got_piranha_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, artifice_core.consts.PIRANHA_IMAGE, font=font, popup=False)

    if got_piranha_image:
        piranha_image_status = 'PIRANHA image installed'
        piranha_text_color = None
    else:
        piranha_image_status = 'PIRANHA image not installed'
        piranha_text_color = '#db4325' #red

    layout = [
    [
    sg.Text(docker_status,size=(30,1),text_color=docker_text_color),
    sg.Button(button_text='Open Docker Site in Browser',key='-DOCKER INSTALL-', visible= docker_installed),
    ],
    [
    sg.Text(rampart_image_status,size=(30,1),text_color=rampart_text_color),
    sg.Button(button_text='Install RAMPART image',key='-RAMPART INSTALL-', visible=not got_rampart_image),
    ],
    [
    sg.Text(piranha_image_status,size=(30,1),text_color=piranha_text_color),
    sg.Button(button_text='Install PIRANHA image',key='-PIRANHA INSTALL-', visible=not got_piranha_image),
    ],
    [sg.Button(button_text='Launch ARTIFICE',key='-LAUNCH-'),],
    ]


    return layout

def create_startup_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    make_theme()
    layout = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    return new_window

def run_startup_window(window, font=None):

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            break

        elif event == '-DOCKER INSTALL-':
            try:
                open_new_tab('https://docs.docker.com/get-docker/')
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-RAMPART INSTALL-':
            try:
                client.images.pull(artifice_core.consts.RAMPART_IMAGE)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-PIRANHA INSTALL-':
            try:
                client.images.pull(artifice_core.consts.PIRANHA_IMAGE)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)


        elif event == '-LAUNCH-':
            window.close()
            return False
