import PySimpleGUI as sg
import os.path
from os import makedirs, mkdir
import sys
import json
import traceback
import time
from datetime import datetime
from shutil import copytree

from artifice_core import consts
from artifice_core.update_log import update_log
import artifice_core.language as language
import advanced_window.main_window
import basic_window.edit_run_window
import basic_window.execute_run_window
import basic_window.about_window
import artifice_core.startup_window
import artifice_core.window_functions as window_functions
from artifice_core.manage_protocols import add_protocol
from artifice_core.window_functions import scale_window, scale_image

#create artifice theme
def make_themes(version):

    consts.THEMES = {
        'DEFAULT': {'BACKGROUND': "#1e5b67",
                'TEXT': '#f7eacd',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#d97168'),
                'BUTTON_HOVER': ('#f7eacd', '#F48379'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0},
        'CONTENT': {'BACKGROUND': "#f7eacd",
                'TEXT': '#1e5b67',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#1e5b67'),
                'BUTTON_HOVER': ('#f7eacd', '#328E9A'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'PANEL': {'BACKGROUND': "#F5F1DF",
                'TEXT': '#1e5b67',
                'INPUT': '#f7eacd',
                'TEXT_INPUT': '#072429',
                'CONSOLE_TEXT': '#FFBF00',
                'CONSOLE_BACKGROUND': '#072429',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#1e5b67'),
                'BUTTON_HOVER': ('#f7eacd', '#328E9A'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'HEADER': {'BACKGROUND': "#1e5b67",
                'TEXT': '#f7eacd',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#d97168'),
                'BUTTON_HOVER': ('#f7eacd', '#F48379'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}
    }

    for key, value in consts.THEMES.items():
        sg.theme_add_new(key, value)


#make sure a directory exists to save runs
def check_runs_dir(runs_dir):
    filepath = runs_dir / 'archived_runs.json'
    if os.path.isfile(filepath):
        return True
    else:
        archived_dict = {"archived_runs": []}

        if not os.path.isdir(runs_dir):
            makedirs(runs_dir)

        with open(filepath, 'w') as file:
            json.dump(archived_dict, file)

# makes sure builtin protocols are installed
def setup_builtin_protocols():
    config = artifice_core.consts.retrieve_config()
    builtin_path = str(artifice_core.consts.get_datadir() / 'builtin_protocols')
    try:
        copytree('builtin_protocols', builtin_path)
    except:
        pass
    
    try:
        mkdir(config['PROTOCOLS_DIR'])
    except:
        pass

    try:
        add_protocol('ARTIC Poliovirus protocol v1.1', str(artifice_core.consts.get_datadir() / 'builtin_protocols' / 'rampart'), config)
    except:
        pass

    try:
        add_protocol('default RAMPART protocol', str(artifice_core.consts.get_datadir() / 'builtin_protocols' / 'default_protocol'), config)
    except:
        pass

def create_splash_window():
    sg.theme('CONTENT')
    
    main_logo_scaled = scale_image(consts.ICON_FILENAME,scale,(150,150))
    
    layout = [
        [sg.Image(source = main_logo_scaled)],
        [sg.Text(language.translator('Starting up..'), font=consts.TITLE_FONT, justification = 'center')]
        ]
    
    window = sg.Window('PiranhaGUI', layout, resizable=False, enable_close_attempted_event=False, finalize=True,
                       icon=consts.ICON)

    return window

if __name__ == '__main__':
    advanced = False
    startup_time = datetime.today()
    check_runs_dir(consts.RUNS_DIR)
    update_log(f'Started ARTIFICE at {startup_time}\n', overwrite = True)
    setup_builtin_protocols()

    language.translator = language.setup_translator()

    scale = scale_window()
    consts.ICON = window_functions.scale_image(consts.ICON_FILENAME, consts.SCALING, (64,64))

    version = consts.VERSION
    make_themes(version)

    splash_window = create_splash_window()
    
    window = artifice_core.startup_window.create_startup_window() #create the startup window to check/install docker and images

    splash_window.close()

    advanced = artifice_core.startup_window.run_startup_window(window)
    
    if advanced != None: # if button pressed to launch artifice
        try:
            if advanced:
                window, rampart_running = advanced_window.main_window.create_main_window()
                advanced_window.main_window.run_main_window(window, rampart_running=rampart_running)
            else:
                while True: # user can go back and forth between editing and executing runs
                    window = basic_window.edit_run_window.create_edit_window()
                    run_info = basic_window.edit_run_window.run_edit_window(window)
                    if run_info == None:
                        break

                    update_log(f'\nrun details confirmed, creating main window\n')
                    window, rampart_running, piranha_running = basic_window.execute_run_window.create_main_window()
                    edit = basic_window.execute_run_window.run_main_window(window, run_info, rampart_running=rampart_running, piranha_running=piranha_running)
                    if edit != True:
                        break
            exit_time = datetime.today()
            update_log(f'\nExited successfully at {exit_time}\n')


        except Exception as err:
            exit_time = datetime.today()
            update_log(traceback.format_exc())
            update_log(f'\nExited unexpectedly at {exit_time}\n')
            print(traceback.format_exc(), file=sys.stderr)
        else:
            window.close()


    else:
        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')
