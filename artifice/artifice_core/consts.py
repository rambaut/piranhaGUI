from yaml import safe_load, safe_dump
from pathlib import Path
import pathlib
import sys
import shutil
import os.path
from os import getenv, cpu_count, mkdir, remove

#returns directory where Artifice stores data, dependent on os
def get_datadir():
    home = pathlib.Path.home()

    if sys.platform.startswith("win"): #windows
        os_path = getenv("LOCALAPPDATA")
    elif sys.platform.startswith("darwin"): #macOS
        os_path = "~/Library/Application Support"
    else: #linux
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    #path = Path(os_path) / "ARTIFICE"
    path = Path(os_path) / "piranhaGUI"

    path = path.expanduser()

    if not os.path.isdir(path): #creates data directory if it doesn't exist
        mkdir(path)

    return path

# checks config file exists, if not creates the config file
def setup_config():
    config_path = str(get_datadir() / 'config.yml')
    if os.path.isfile(config_path):
        return True
    else:
        shutil.copyfile('./config.yml', config_path)

# reset config to defaults
def set_config_to_default():
    config_path = str(get_datadir() / 'config.yml')
    if os.path.isfile(config_path):
        remove(config_path)
    shutil.copyfile('./config.yml', config_path)

# returns a dict with config value taken from the config file
def retrieve_config():
    config_path = str(get_datadir() / 'config.yml')
    with open(config_path) as file:
        config = safe_load(file)

    config['RUNS_DIR'] = get_datadir() / 'runs'
    config['PROTOCOLS_DIR'] = get_datadir() / 'protocols'
    config['CONSOLE_FONT'] = 'Consolas'

    THREADS = config['THREADS'] #how many threads piranha should use
    if THREADS == None:
        THREADS = max(int(cpu_count()/2),1)
        if THREADS == None:
            THREADS = 1

    config['THREADS'] = THREADS

    if 'LANGUAGE' not in config:
        config['LANGUAGE'] = 'English'

    if 'PROTOCOL' not in config:
        config['PROTOCOL'] = 'ARTIC Poliovirus protocol v1.1' #'default RAMPART protocol'#

    if 'VERSION' not in config:
        config['VERSION'] = 'piranhaGUI'
    
    return config

# edits the value of one config value
def edit_config(key, value):
    config_path = str(get_datadir() / 'config.yml')
    with open(config_path) as file:
        config = safe_load(file)

    config[key] = value

    with open(config_path, 'w') as file:
        safe_dump(config, file)
          
def get_theme(key):
    if THEMES[key] != None:
        return THEMES[key]
    else:
        return THEMES['DEFAULT']

setup_config()
config = retrieve_config()

RAMPART_PORT_1 = config['RAMPART_PORT_1']
RAMPART_PORT_2 = config['RAMPART_PORT_2']
ARCHIVED_RUNS = config['ARCHIVED_RUNS']
RUNS_DIR = config['RUNS_DIR']
RAMPART_IMAGE = config['RAMPART_IMAGE']
RAMPART_LOGFILE = config['RAMPART_LOGFILE']
PIRANHA_IMAGE = config['PIRANHA_IMAGE']
PIRANHA_LOGFILE = config['PIRANHA_LOGFILE']
LOGFILE = config['LOGFILE']
#FIRST_TIME_SETUP = config['FIRST_TIME_SETUP']
THREADS = config['THREADS']
VERSION = config['VERSION']
SCALING = config['SCALING']

# styling constants
BUTTON_SIZE = (120,24)
BUTTON_FONT_FAMILY = 'Helvetica'
BUTTON_FONT_SIZE = 18
BUTTON_FONT = (BUTTON_FONT_FAMILY, BUTTON_FONT_SIZE)
DEFAULT_FONT_FAMILY = 'Helvetica'
DEFAULT_FONT_SIZE = 18
DEFAULT_FONT = (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
MONOTYPE_FONT_FAMILY = 'Consolas'
MONOTYPE_FONT_SIZE = 18
CONSOLE_FONT = (MONOTYPE_FONT_FAMILY, MONOTYPE_FONT_SIZE)

# piranhna options
VALUE_POSITIVE = config['VALUE_POSITIVE']
VALUE_NEGATIVE = config['VALUE_NEGATIVE']
VALUE_SAMPLE_TYPE = config['VALUE_SAMPLE_TYPE']
VALUE_MIN_MAP_QUALITY = ['VALUE_MIN_MAP_QUALITY']
VALUE_MIN_READ_LENGTH = ['VALUE_MIN_READ_LENGTH']
VALUE_MAX_READ_LENGTH = ['VALUE_MIN_READ_LENGTH']
VALUE_MIN_READS = ['VALUE_MIN_READS']
VALUE_MIN_PCENT = ['VALUE_MIN_PCENT']
VALUE_PRIMER_LENGTH = ['VALUE_PRIMER_LENGTH']
VALUE_OUTPUT_PREFIX = ['VALUE_OUTPUT_PREFIX']


THEMES = { }

if __name__ == '__main__':
    #home = pathlib.Path.home()
    print(RUNS_DIR)
