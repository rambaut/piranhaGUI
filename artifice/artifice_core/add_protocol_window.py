import PySimpleGUI as sg

import artifice_core.consts
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

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
    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'


    button_size=(120,36)
    layout = [
    [sg.Text(translate_text('Select the protocol directory:',language,translate_scheme),),],
    [
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-PROTOCOL DIR-',),
    AltFolderBrowse(button_text=translate_text('Browse',language,translate_scheme),font=font,size=button_size),
    ],
    [AltButton(button_text=translate_text('Confirm',language,translate_scheme),size=button_size,font=font,key='-CONFIRM-'),],
    ]

    return layout

def create_add_protocol_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating add protocol window')
    make_theme()
    layout = setup_layout(theme=theme, font=font)
    piranha_scaled = scale_image('piranha.png',scale,(64,64))
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=piranha_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_add_protocol_window(window, font = None, version = 'ARTIFICE'):
    config = artifice_core.consts.retrieve_config()
    
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [add protocol window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

       
        elif event == '-CONFIRM-':
            try:
                window.close()
                return values['-PROTOCOL DIR-']
            except Exception as err:
                error_popup(err, font)

    window.close()