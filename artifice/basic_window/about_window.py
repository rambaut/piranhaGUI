import PySimpleGUI as sg

import artifice_core.parse_columns_window
import artifice_core.consts
import artifice_core.start_rampart
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

def setup_panel(translator, font = None):
    sg.theme("PANEL")
    column = [
                [sg.Text('Piranha', font=('Helvetica Neue Light', 18), expand_x=True)],
                [sg.Text('Áine O’Toole, Rachel Colquhoun, Corey Ansley, Zoe Vance & Andrew Rambaut', font=('Helvetica Neue Light', 14))],
                [sg.Text('\nPiranhaGUI', font=('Helvetica Neue Light', 18), expand_x=True)],
                [sg.Text('Corey Ansley & Andrew Rambaut', font=('Helvetica Neue Light', 14))],
                [sg.Text('\nPolio Direct Detection by Nanopore Sequencing (DDNS)', font=('Helvetica Neue Light', 18))],
                [sg.Text('Alexander G. Shaw, Manasi Majumdar, Catherine Troman, Áine O’Toole, Blossom Benny, '+
                        'Dilip Abraham, Ira Praharaj, Gagandeep Kang, Salmaan Sharif, Muhammad Masroor Alam, '+
                        'Shahzad Shaukat, Mehar Angez, Adnan Khurshid, Nayab Mahmood, Yasir Arshad, Lubna Rehman, '+
                        'Ghulam Mujtaba, Ribqa Akthar, Muhammad Salman, Dimitra Klapsa, Yara Hajarha, Humayun Asghar, '+
                        'Ananda Bandyopadhyay, Andrew Rambaut, Javier Martin, Nicholas Grassly', size=(96, None), font=('Helvetica Neue Light', 14))],
            ]
    

    panel = sg.Frame("Credits", [[
        sg.Column([[
                sg.Column(column, size=(None, 256), vertical_alignment='Top', expand_x=True, scrollable=True, vertical_scroll_only=True)
            ]], pad=(16,0), expand_x=True)]], border_width=0, relief="solid", pad=(0,16), expand_x=True)

    return panel

def create_about_window(version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating about window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    panel = setup_panel(translator, font = font)

    content = artifice_core.window_functions.setup_content(panel, translator, button_text='Close', button_key='Exit')

    layout = artifice_core.window_functions.setup_header_footer(content, large=True)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
   
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_about_window(window, font = None, version = 'ARTIFICE'):
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

    window.close()


