import PySimpleGUI as sg
import traceback

import artifice_core.consts as consts
from artifice_core.language import translator, get_translate_scheme
import artifice_core.window_functions as window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup, scale_window

# Options window to allow user to modify certain config values

def setup_panel():
    sg.theme("PANEL")

    translate_scheme = get_translate_scheme()
    try:
        language = consts.config['LANGUAGE']
    except:
        language = 'English'

    languages = translate_scheme[0]

    column1 = [[
            sg.Sizer(0,48),
            sg.Push(),
            sg.Text(translator('Select language for user-interface: ')),
        ],[
            sg.Sizer(0,48),
            sg.Push(),
            sg.Text(translator('Use of RAMPART for real-time monitoring of sequencing: ')),
        ]
        ]

    column2 = [[
            sg.Sizer(0,48),
            sg.InputCombo(languages, default_value=language, readonly=True, key='-LANGUAGE SELECT-'),
        ],[
            sg.Sizer(0,48),
            sg.Checkbox(translator('Enabled'),default=consts.config['SHOW_RAMPART'],key='-SHOW RAMPART-')
        ]]

    layout = [[
        sg.Column([[
            sg.Column(column1), 
            sg.Column(column2)
        ]],pad=(16,0))]]
    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

    return panel

def create_options_window(window = None, version='ARTIFICE'):
    update_log(f'opening options window')

    panel = setup_panel()

    content = window_functions.setup_content(panel, small=True, button_text='Save', button_key='-SAVE-',
                                             bottom_left_button_text='Reset', bottom_left_button_key='-RESET CONFIG-')

    layout = window_functions.setup_header_footer(content, small=True)

    new_window = sg.Window(version, layout, resizable=False, finalize=True,icon=consts.ICON, font=consts.DEFAULT_FONT,
                                                      margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_options_window(window):
    while True:
        config = consts.retrieve_config()
        event, values = window.read()
        if event != None:
            log_event(f'{event} [options window]')

        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            return True
            break
        elif event == '-RESET CONFIG-':
            consts.set_config_to_default()
            scale_window()
        elif event == '-SAVE-':
            try:
                if values['-LANGUAGE SELECT-'] != config['LANGUAGE']:
                    consts.edit_config('LANGUAGE', values['-LANGUAGE SELECT-'])
                if values['-SHOW RAMPART-'] != config['SHOW_RAMPART']:
                    consts.edit_config('SHOW_RAMPART', values['-SHOW RAMPART-'])
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
