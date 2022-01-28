import os.path
from os import makedirs
import json
from datetime import datetime

import consts
import main_window
import selection_window
import parse_columns_window
import start_rampart
import view_barcodes_window
from update_log import update_log

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



if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (consts.FONT, 18)
    check_runs_dir(consts.RUNS_DIR)

    startup_time = datetime.today()
    update_log(f'Started ARTIFICE at {startup_time}\n', overwrite = True)


    #update_log(test_string)
    #print('a'*200)

    window, rampart_running = main_window.create_main_window(font=font)
    main_window.run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()

    exit_time = datetime.today()
    update_log(f'\nExited successfully at {exit_time}\n', overwrite = False)
