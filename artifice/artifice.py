import PySimpleGUI as sg
import os.path
from os import makedirs
import json
from datetime import datetime
import traceback

import artifice_core.consts
from artifice_core.update_log import update_log
import advanced_window.main_window
import basic_window.edit_run_window
import basic_window.execute_run_window
import artifice_core.startup_window

def make_theme(poseqco_scheme=True):
    if poseqco_scheme:
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
    else:
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

def check_runs_dir(runs_dir):
    filepath = runs_dir + '/archived_runs.json'
    if os.path.isfile(filepath):
        return True
    else:
        archived_dict = {"archived_runs": []}

        if not os.path.isdir(runs_dir):
            makedirs(runs_dir)

        with open(filepath, 'w') as file:
            json.dump(archived_dict, file)

def scale_window(font=None):
    layout = [[sg.Text('setting up..')]]
    window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)
    resolution = window.get_screen_dimensions()[1]
    scale = resolution/1080
    update_log(f'scaling by {scale}')
    sg.set_options(scaling=scale)
    window.close()

if __name__ == '__main__':
    advanced = False
    startup_time = datetime.today()
    update_log(f'Started ARTIFICE at {startup_time}\n', overwrite = True)

    font = (artifice_core.consts.FONT, 18)

    scale_window()
    make_theme()
    window = artifice_core.startup_window.create_startup_window(font=font)
    advanced = artifice_core.startup_window.run_startup_window(window, font=font)

    if advanced != None:
        try:
            if advanced:
                check_runs_dir(artifice_core.consts.RUNS_DIR)
                window, rampart_running = advanced_window.main_window.create_main_window(font=font)
                advanced_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)
            else:
                #window, rampart_running = basic_window.main_window.create_main_window(font=font)
                #basic_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)
                while True:
                    window = basic_window.edit_run_window.create_edit_window(font=font)
                    run_info = basic_window.edit_run_window.run_edit_window(window, font=font)
                    if run_info == None:
                        break

                    update_log(f'\nrun details confirmed, creating main window\n')
                    window, rampart_running = basic_window.execute_run_window.create_main_window(font=font)
                    edit = basic_window.execute_run_window.run_main_window(window, run_info, font=font, rampart_running=rampart_running)
                    if edit != True:
                        break


        except Exception as err:
            exit_time = datetime.today()
            update_log(traceback.format_exc())
            update_log(f'\nExited unexpectedly at {exit_time}\n')
        else:
            window.close()

        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')

    else:
        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')
