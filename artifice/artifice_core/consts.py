from yaml import safe_load
from pathlib import Path
import pathlib
import sys
from os import getenv, cpu_count

def retrieve_config():
    with open('./config.yml') as file:
        config = safe_load(file)

    return config

#returns directory where Artifice stores data, dependent on os
def get_datadir():

    home = pathlib.Path.home()

    if sys.platform.startswith("win"): #windows
        os_path = getenv("LOCALAPPDATA")
    elif sys.platform.startswith("darwin"): #macOS
        os_path = "~/Library/Application Support"
    else: #linuxWomen’s Health Innovation Forum Scotland conference - 24 & 25 March 2022
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    path = Path(os_path) / "ARTIFICE"

    return path.expanduser() #/ file_name



config = retrieve_config()

RAMPART_PORT_1 = config['RAMPART_PORT_1']
RAMPART_PORT_2 = config['RAMPART_PORT_2']
ARCHIVED_RUNS = config['ARCHIVED_RUNS']
RUNS_DIR = str(get_datadir() / 'runs')
RAMPART_IMAGE = config['RAMPART_IMAGE']
RAMPART_LOGFILE = config['RAMPART_LOGFILE']
PIRANHA_IMAGE = config['PIRANHA_IMAGE']
PIRANHA_LOGFILE = config['PIRANHA_LOGFILE']
FONT = config['FONT']
LOGFILE = config['LOGFILE']


THREADS = config['THREADS'] #how many threads piranha should use
if THREADS == None:
    THREADS = cpu_count()
    if THREADS == None:
        THREADS = 1
#BACKGROUND_COLOR = "#072429"

if __name__ == '__main__':
    #home = pathlib.Path.home()
    print(RUNS_DIR)
