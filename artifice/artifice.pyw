import PySimpleGUI as sg
import os.path
from os import makedirs, mkdir
import json
import traceback
import time
from datetime import datetime
from shutil import copytree

import artifice_core.consts
from artifice_core.update_log import update_log
import advanced_window.main_window
import basic_window.edit_run_window
import basic_window.execute_run_window
import artifice_core.startup_window
from artifice_core.manage_protocols import add_protocol
from artifice_core.window_functions import scale_window, scale_image

#create artifice theme
def make_theme(version):
    if version == 'piranhaGUI': # poseqco color scheme
        Artifice_Theme = {'BACKGROUND': "#FBECA6",
                   'TEXT': '#000000',
                   'INPUT': '#FFAE59',
                   'TEXT_INPUT': '#000000',
                   'SCROLL': '#707070',
                   'BUTTON': ('#FEAE63', '#FF4600'),
                   'PROGRESS': ('#000000', '#000000'),
                   'BORDER': 1,
                   'SLIDER_DEPTH': 0,
                   'PROGRESS_DEPTH': 0}

    else: # artic color scheme
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

def create_setup_window(scale, version):
    sg.theme('Artifice')
    is_piranhaGUI = version.startswith('piranhaGUI')

     # Resize PNG file to appropiate size
    if is_piranhaGUI:
        main_logo_scaled = scale_image('piranha.png',scale,(150,150))
    else:
        main_logo_scaled = scale_image('a_logo.png',scale,(100,120))

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
    
    layout = [
        [sg.Image(source = main_logo_scaled)],
        [sg.Text('setting up..', justification = 'center')]
        ]
    
    window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled)

    return window

if __name__ == '__main__':
    advanced = False
    startup_time = datetime.today()
    check_runs_dir(artifice_core.consts.RUNS_DIR)
    update_log(f'Started ARTIFICE at {startup_time}\n', overwrite = True)
    setup_builtin_protocols()

    font = (artifice_core.consts.FONT, 18)

    scale = scale_window()
    version = artifice_core.consts.VERSION
    make_theme(version)
    window = create_setup_window(scale, version)

    
    window = artifice_core.startup_window.create_startup_window(font=font, scale=scale, version=version, window=window) #create the startup window to check/install docker and images
    advanced = artifice_core.startup_window.run_startup_window(window, font=font, scale=scale, version=version)
    make_theme('artifice')

    if advanced != None: # if button pressed to launch artifice
        try:
            if advanced:
                window, rampart_running = advanced_window.main_window.create_main_window(font=font)
                advanced_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)
            else:
                while True: # user can go back and forth between editing and executing runs
                    window = basic_window.edit_run_window.create_edit_window(font=font, scale=scale, version=version)
                    run_info = basic_window.edit_run_window.run_edit_window(window, font=font, version=version)
                    if run_info == None:
                        break

                    update_log(f'\nrun details confirmed, creating main window\n')
                    window, rampart_running, piranha_running = basic_window.execute_run_window.create_main_window(font=font, scale=scale, version=version)
                    edit = basic_window.execute_run_window.run_main_window(window, run_info, font=font, rampart_running=rampart_running, piranha_running=piranha_running, scale=scale, version=version)
                    if edit != True:
                        break
            exit_time = datetime.today()
            update_log(f'\nExited successfully at {exit_time}\n')


        except Exception as err:
            exit_time = datetime.today()
            update_log(traceback.format_exc())
            update_log(f'\nExited unexpectedly at {exit_time}\n')
        else:
            window.close()


    else:
        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')
