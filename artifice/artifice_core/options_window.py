import PySimpleGUI as sg
import traceback
from os import cpu_count

import artifice_core.consts
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

# Options window to allow user to modify certain config values

def setup_options_layout(theme = 'Dark', font = None, version='ARTIFICE'):
    config = artifice_core.consts.retrieve_config()
    sg.theme(theme)

    threads_list = range(1, cpu_count()+1)

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    languages = translate_scheme[0]

    is_piranhaGUI = version.startswith('piranhaGUI')

    layout = [
        [
        sg.Text(translate_text('Threads to use for analysis:',language,translate_scheme),visible=is_piranhaGUI,size=(30,1)),
        sg.OptionMenu(threads_list, default_value=config['THREADS'],visible=is_piranhaGUI, key='-THREADS SELECT-'),
        ],
        [
        sg.Text(translate_text('Select language:',language,translate_scheme),size=(30,1)),
        sg.OptionMenu(languages, default_value=language, key='-LANGUAGE SELECT-'),
        ],
        [
        AltButton(button_text=translate_text('Save',language,translate_scheme), font=font,key='-SAVE-'),
        ],
    ]

    return layout

def create_options_window(theme = 'Artifice', font = None, window = None, scale = 1, version='ARTIFICE'):
    update_log(f'opening options window')
    layout = setup_options_layout(theme=theme, font=font, version=version)
    piranha_scaled = scale_image('piranha.png',scale,(64,64))
    new_window = sg.Window(version, layout, font=font, resizable=False, finalize=True,icon=piranha_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_options_window(window, font):
    while True:
        config = artifice_core.consts.retrieve_config()
        event, values = window.read()
        if event != None:
            log_event(f'{event} [options window]')

        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            return True
            break
        elif event == '-SAVE-':
            try:
                if values['-THREADS SELECT-'] != config['THREADS']:
                    artifice_core.consts.edit_config('THREADS', values['-THREADS SELECT-'])
                if values['-LANGUAGE SELECT-'] != config['LANGUAGE']:
                    artifice_core.consts.edit_config('LANGUAGE', values['-LANGUAGE SELECT-'])
                window.close()
                return True
                break
            except Exception as err:
                error_popup(err, font)

    window.close()
    return None

if __name__ == '__main__':

    window = create_options_window()
    run_options_window(window)

    window.close()
