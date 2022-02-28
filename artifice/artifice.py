import PySimpleGUI as sg
import os.path
from os import makedirs
import json
from datetime import datetime
import traceback

import artifice_core.consts
from artifice_core.update_log import update_log
import advanced_window.main_window
import basic_window.main_window

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

    #update_log(test_string)
    #print('a'*200)

    scale_window()
    try:
        if advanced:
            check_runs_dir(artifice_core.consts.RUNS_DIR)
            window, rampart_running = advanced_window.main_window.create_main_window(font=font)
            advanced_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)
        else:
            window, rampart_running = basic_window.main_window.create_main_window(font=font)
            basic_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)
    except Exception as err:
        exit_time = datetime.today()
        update_log(traceback.format_exc())
        update_log(f'\ncExited unexpectedly at {exit_time}')
    else:
        window.close()

        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')
