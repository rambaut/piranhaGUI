from yaml import safe_load, safe_dump
from pathlib import Path
import pathlib
import sys
import csv
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

def get_config_value(key, config):
    try:
        value = config[key]
    except:
        with open('./config.yml') as file:
            default_config = safe_load(file)
            value = default_config[key]
            edit_config(key, value)
    
    return value
                  
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

RAMPART_PORT_1 = get_config_value('RAMPART_PORT_1', config)
RAMPART_PORT_2 = get_config_value('RAMPART_PORT_2', config)
ARCHIVED_RUNS = get_config_value('ARCHIVED_RUNS', config)
RUNS_DIR = get_config_value('RUNS_DIR', config)
RAMPART_IMAGE = get_config_value('RAMPART_IMAGE', config)
RAMPART_LOGFILE = get_config_value('RAMPART_LOGFILE', config)
SHOW_RAMPART = get_config_value('SHOW_RAMPART', config)
PIRANHA_IMAGE = get_config_value('PIRANHA_IMAGE', config)
PIRANHA_LOGFILE = get_config_value('PIRANHA_LOGFILE', config)
LOGFILE = get_config_value('LOGFILE', config)
#FIRST_TIME_SETUP = get_config_value('FIRST_TIME_SETUP', config)
THREADS = get_config_value('THREADS', config)
VERSION = get_config_value('VERSION', config)
SCALING = get_config_value('SCALING', config)

ICON_FILENAME = 'piranha.png'
ICON = None

# styling constants
BUTTON_SIZE = (128,32)
BUTTON_FONT_FAMILY = 'Helvetica Neue Light'
BUTTON_FONT_SIZE = 14
BUTTON_FONT = (BUTTON_FONT_FAMILY, BUTTON_FONT_SIZE)

DEFAULT_FONT_FAMILY = 'Helvetica Neue Light'
DEFAULT_FONT_SIZE = 16
DEFAULT_FONT = (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
MONOTYPE_FONT_FAMILY = 'Consolas'
CONSOLE_FONT_SIZE = 16
CONSOLE_FONT = (MONOTYPE_FONT_FAMILY, CONSOLE_FONT_SIZE)

HEADER_TITLE_FONT = ('Helvetica Neue Thin', 24)
HEADER_FONT = (DEFAULT_FONT_FAMILY, 18)
FOOTER_FONT = (DEFAULT_FONT_FAMILY, 14)

TITLE_FONT = ('Helvetica Neue Thin', 24)
SUBTITLE_FONT = (DEFAULT_FONT_FAMILY, 18)

# piranhna options
VALUE_POSITIVE =  get_config_value('VALUE_POSITIVE', config)
VALUE_NEGATIVE = get_config_value('VALUE_NEGATIVE', config)
VALUE_SAMPLE_TYPE = get_config_value('VALUE_SAMPLE_TYPE', config)
VALUE_MIN_MAP_QUALITY = get_config_value('VALUE_MIN_MAP_QUALITY', config)
VALUE_MIN_READ_LENGTH = get_config_value('VALUE_MIN_READ_LENGTH', config)
VALUE_MAX_READ_LENGTH = get_config_value('VALUE_MIN_READ_LENGTH', config)
VALUE_MIN_READS = get_config_value('VALUE_MIN_READS', config)
VALUE_MIN_PCENT = get_config_value('VALUE_MIN_PCENT', config)
VALUE_PRIMER_LENGTH = get_config_value('VALUE_PRIMER_LENGTH', config)
VALUE_OUTPUT_PREFIX = get_config_value('VALUE_OUTPUT_PREFIX', config)

config = retrieve_config()

THEMES = { }

if __name__ == '__main__':
    #home = pathlib.Path.home()
    print(RUNS_DIR)
