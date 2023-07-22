import PySimpleGUI as sg

from artifice_core.language import translator
import artifice_core.consts as consts
import artifice_core.window_functions as window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup

def setup_panel():
    sg.theme("PANEL")
    column = [
                [sg.Text('Piranha', font=(None, 18), expand_x=True)],
                [sg.Text('Áine O’Toole, Rachel Colquhoun, Corey Ansley, Zoe Vance & Andrew Rambaut', font=(None, 14))],
                [sg.Text('\nPiranhaGUI', font=(None, 18), expand_x=True)],
                [sg.Text('Corey Ansley & Andrew Rambaut', font=(None, 14))],
                [sg.Text('\nPolio Direct Detection by Nanopore Sequencing (DDNS)', font=(None, 18))],
                [sg.Text('Alexander G. Shaw, Manasi Majumdar, Catherine Troman, Áine O’Toole, Blossom Benny, '+
                        'Dilip Abraham, Ira Praharaj, Gagandeep Kang, Salmaan Sharif, Muhammad Masroor Alam, '+
                        'Shahzad Shaukat, Mehar Angez, Adnan Khurshid, Nayab Mahmood, Yasir Arshad, Lubna Rehman, '+
                        'Ghulam Mujtaba, Ribqa Akthar, Muhammad Salman, Dimitra Klapsa, Yara Hajarha, Humayun Asghar, '+
                        'Ananda Bandyopadhyay, Andrew Rambaut, Javier Martin, Nicholas Grassly', size=(96, None), font=(None, 14))],
            ]
    

    panel = sg.Column([[
            sg.Frame("Credits", [[
                sg.Column(column, size=(None, 256), vertical_alignment='Top',  pad=(16,0), expand_x=True, 
                          scrollable=True, vertical_scroll_only=True)
            ]], font=consts.SUBTITLE_FONT, border_width=0, relief="solid", pad=(16,0), expand_x=True)]], 
            pad=(0,16), expand_x=True)

    return panel

def create_about_window(version = 'ARTIFICE', window = None):
    update_log('creating about window')

    panel = setup_panel()

    content = window_functions.setup_content(panel, button_text='Close', button_key='Exit')

    layout = window_functions.setup_header_footer(content, large=True)

    new_window = sg.Window(version, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_about_window(window, version = 'ARTIFICE'):
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

    window.close()


