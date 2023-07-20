import PySimpleGUI as sg
import traceback
from os import cpu_count

import artifice_core.consts as consts
import artifice_core.window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image, scale_window

# Options window to allow user to modify certain config values

def setup_panel():
    sg.theme("PANEL")

    config = consts.retrieve_config()

    threads_list = range(1, cpu_count()+1)

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    languages = translate_scheme[0]

    layout = [
        [
        sg.Text(translate_text('Threads to use for analysis:',language,translate_scheme),size=(30,1)),
        sg.OptionMenu(threads_list, default_value=config['THREADS'], key='-THREADS SELECT-'),
        ],
        [
        sg.Text(translate_text('Select language:',language,translate_scheme),size=(30,1)),
        sg.OptionMenu(languages, default_value=language, key='-LANGUAGE SELECT-'),
        ],
        [
        sg.Checkbox(translate_text('Enable/Disable RAMPART',language,translate_scheme),default=config['SHOW_RAMPART'],size=(30,1),key='-SHOW RAMPART-')
        ],
        [
        AltButton(button_text=translate_text('Reset config to default',language,translate_scheme), font=font,key='-RESET CONFIG-'),
        ],
        # [
        # AltButton(button_text=translate_text('Save',language,translate_scheme), font=font,key='-SAVE-'),
        # ],
    ]

    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

    return panel

def create_options_window(theme = 'Artifice', window = None, version='ARTIFICE'):
    update_log(f'opening options window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    panel = setup_panel()

    content = artifice_core.window_functions.setup_content(panel, translator, small=True, button_text='Save', button_key='-SAVE-')

    layout = artifice_core.window_functions.setup_header_footer(content, small=True)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',1,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',1,(64,64))
    
    new_window = sg.Window(version, layout, resizable=False, finalize=True,icon=icon_scaled,
                                                      margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_options_window(window):
    while True:
        config = artifice_core.consts.retrieve_config()
        event, values = window.read()
        if event != None:
            log_event(f'{event} [options window]')

        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            return True
            break
        elif event == '-RESET CONFIG-':
            artifice_core.consts.set_config_to_default()
            scale_window()
        elif event == '-SAVE-':
            try:
                if values['-THREADS SELECT-'] != config['THREADS']:
                    artifice_core.consts.edit_config('THREADS', values['-THREADS SELECT-'])
                if values['-LANGUAGE SELECT-'] != config['LANGUAGE']:
                    artifice_core.consts.edit_config('LANGUAGE', values['-LANGUAGE SELECT-'])
                if values['-SHOW RAMPART-'] != config['SHOW_RAMPART']:
                    artifice_core.consts.edit_config('SHOW_RAMPART', values['-SHOW RAMPART-'])
                window.close()
                return True
                break
            except Exception as err:
                error_popup(err)

    window.close()
    return None

if __name__ == '__main__':

    window = create_options_window()
    run_options_window(window)

    window.close()
