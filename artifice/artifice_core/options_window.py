import PySimpleGUI as sg
import traceback
from os import cpu_count

import artifice_core.consts
from artifice_core.update_log import log_event, update_log

def setup_options_layout(theme = 'Dark'):
    config = artifice_core.consts.retrieve_config()
    sg.theme(theme)
    threads_list = range(1, cpu_count()+1)
    layout = [
        [
        sg.Text('Threads to use for Piranha',size=(25,1)),
        sg.OptionMenu(threads_list, default_value=config['THREADS'], key='-THREADS SELECT-'),
        ],
        [
        sg.Button(button_text='Save',key='-SAVE-'),
        ],
    ]

    return layout

def create_options_window(theme = 'Artifice', font = None, window = None):
    update_log(f'opening options window')
    layout = setup_options_layout(theme=theme)
    new_window = sg.Window('Artifice', layout, font=font, resizable=False)

    if window != None:
        window.close()

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
        elif event == '-SAVE-':
            try:
                if values['-THREADS SELECT-'] != config['THREADS']:
                    artifice_core.consts.edit_config('THREADS', values['-THREADS SELECT-'])
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    window.close()
    return None

if __name__ == '__main__':

    window = create_options_window()
    run_options_window(window)

    window.close()
