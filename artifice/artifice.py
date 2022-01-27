import os.path
from os import mkdir
import json

import consts
import main_window
import selection_window
import parse_columns_window
import start_rampart
import view_barcodes_window

def check_runs_dir(runs_dir):
    filepath = runs_dir + '/archived_runs.json'
    if os.path.isfile(filepath):
        return True
    else:
        archived_dict = {"archived_runs": []}

        #if not os.path.isdir(runs_dir):
        #    mkdir(runs_dir)

        with open(filepath, 'w') as file:
            json.dump(archived_dict, file)

if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (consts.FONT, 18)
    check_runs_dir(consts.RUNS_DIR)

    window, rampart_running = main_window.create_main_window(font=font)
    main_window.run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
