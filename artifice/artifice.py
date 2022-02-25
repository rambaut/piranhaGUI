import PySimpleGUI as sg
import os.path
from os import makedirs
import json
from datetime import datetime

import artifice_core.consts
from artifice_core.update_log import update_log
import advanced_window.main_window

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
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (artifice_core.consts.FONT, 18)
    check_runs_dir(artifice_core.consts.RUNS_DIR)

    startup_time = datetime.today()
    update_log(f'Started ARTIFICE at {startup_time}\n', overwrite = True)


    #update_log(test_string)
    #print('a'*200)
    #sg.set_options(scaling=1.0)
    scale_window()
    window, rampart_running = advanced_window.main_window.create_main_window(font=font)
    advanced_window.main_window.run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()

    exit_time = datetime.today()
    update_log(f'\nExited successfully at {exit_time}\n', overwrite = False)
