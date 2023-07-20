from pydoc import doc
from turtle import update
import PySimpleGUI as sg
import docker
import traceback
import os.path
import sys
import os
import subprocess
from os import system, mkdir
from webbrowser import open_new_tab
from PIL import Image
from time import sleep

import artifice_core.start_rampart
import artifice_core.consts
import artifice_core.window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.options_window import create_options_window, run_options_window
from artifice_core.alt_button import AltButton
from artifice_core.alt_popup import alt_popup
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

PASS_TEXT_COLOUR = '#1E707E' #blueish '#00bd00'<-green
FAIL_TEXT_COLOUR = '#FF0000' #'#db4325' #red

def setup_panel(translator, font = None):
    sg.theme("PANEL")
    config = artifice_core.consts.retrieve_config()
    docker_client = None

    is_piranhaGUI = True

    docker_installed = artifice_core.start_rampart.check_for_docker(popup=False) #check docker is installed
    if docker_installed:
        docker_status = translator('Docker installed')
        docker_text_color =  PASS_TEXT_COLOUR
    else:
        docker_status = translator('Docker not installed/not running')
        docker_text_color = FAIL_TEXT_COLOUR
    
    got_rampart_image, docker_client, rampart_update_available, rampart_image_status, rampart_pull_text, rampart_text_color = set_image_status('RAMPART',translator,artifice_core.consts.RAMPART_IMAGE,font,check_for_updates=False,docker_client=docker_client)

    got_piranha_image, docker_client, piranha_update_available, piranha_image_status, piranha_pull_text, piranha_text_color = set_image_status('PIRANHA',translator,artifice_core.consts.PIRANHA_IMAGE,font,docker_client=docker_client)

    if is_piranhaGUI:
        if not got_piranha_image:
            # attempt to install piranha image from file

            image_file_path = str(artifice_core.consts.get_datadir() / 'piranha.tar')
            #image_file_path = './resources/piranha.tar'
            if os.path.exists(image_file_path):
                try:
                    with open(image_file_path, 'rb') as image_file:
                        docker_client.images.load(image_file)
                        os.remove(image_file_path) # delete image file now that we're done with it
                except Exception as err:
                    update_log(err)
                    update_log('unable to load PIRANHA image from file')

                got_piranha_image, docker_client, piranha_update_available, piranha_image_status, piranha_pull_text, piranha_text_color = set_image_status('PIRANHA',language,translate_scheme,artifice_core.consts.PIRANHA_IMAGE,font,docker_client=docker_client)

    image_info_text = 'An internet connection and a Docker install is required to install RAMPART and PIRANHA images'

    if is_piranhaGUI and not got_piranha_image:
        show_piranha_button = True

    elif is_piranhaGUI and piranha_update_available:
        show_piranha_button = True
    else:
        show_piranha_button = False

    if rampart_update_available or not got_rampart_image:
        show_rampart_button = True
    else:
        show_rampart_button = False
    
    if 'SHOW_RAMPART' in config:
        SHOW_RAMPART = config['SHOW_RAMPART']
    else:
        if is_piranhaGUI:
            SHOW_RAMPART = False
        else:
            SHOW_RAMPART = True
        
        artifice_core.consts.edit_config('SHOW_RAMPART', SHOW_RAMPART)
    
    show_rampart_text = SHOW_RAMPART
    if SHOW_RAMPART == False:
        show_rampart_button = False

    install_buttons_size = (480,36)
    layout = [
    [sg.Text(translator(image_info_text))],
    [
    sg.Text(docker_status,size=(35,1),text_color=docker_text_color, key='-DOCKER STATUS-'),
    AltButton(button_text=translator('Open Docker Site in Browser'),font=font,size=install_buttons_size,key='-DOCKER INSTALL-', visible=not docker_installed),
    ],
    [
    sg.Text(rampart_image_status,size=(35,1),text_color=rampart_text_color,visible=show_rampart_text,key='-RAMPART IMAGE STATUS-'),
    AltButton(button_text=rampart_pull_text,size=install_buttons_size,visible=show_rampart_button,font=font,key='-RAMPART INSTALL-'),
    ],

    [
    sg.Text(piranha_image_status,size=(35,1),text_color=piranha_text_color,visible=is_piranhaGUI,key='-PIRANHA IMAGE STATUS-'),
    AltButton(button_text=piranha_pull_text,size=install_buttons_size,font=font,visible=show_piranha_button,key='-PIRANHA INSTALL-'),
    ],
    [sg.VPush()],
    [
    AltButton(button_text=translator('Continue'),font=font,key='-LAUNCH-'),
    sg.Push(),
    AltButton(button_text=translator('Options'),font=font,key='-OPTIONS-')
    ],
    ]

    return sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

def create_startup_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating startup window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    panel = setup_panel(translator, font = font)

    content = artifice_core.window_functions.setup_content(panel, translator, button_text='Continue', button_key='-LAUNCH-')

    layout = artifice_core.window_functions.setup_header_footer(content)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
        
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,use_custom_titlebar=False,icon=icon_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

# popup to show user while pulling image
def create_install_popup(name, font):
    sg.theme('Artifice')
    inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    install_popup = sg.Window('', [[inst_frame]], disable_close=True, finalize=True,
                                font=font, resizable=False, no_titlebar=True,)
    install_popup.read(timeout=100)
    return install_popup

# creates an alternate config file for docker. Used as a workaround for issue #16
def create_alt_docker_config():
    if sys.platform.startswith("darwin"):
        filepath = f"{os.getenv('HOME')}/.docker/config.json"
        with open(filepath, mode='r') as file:
            file_data = file.read()
        replace_data = file_data.replace('credsStore','credStore')

        docker_data_dir = artifice_core.consts.get_datadir() / 'docker'
        try:
            mkdir(docker_data_dir)
        except FileExistsError:
            print('y')

        alt_config_filepath = docker_data_dir / 'config.json'
        update_log('creating alternate fixed docker config')
        with open(alt_config_filepath, mode='w') as file:
            file.write(replace_data)

# set up image status text and button after checking if image is installed/up to date
def set_image_status(name, translator, image, font, check_for_updates = True, docker_client = None):
    got_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, image, font=font, popup=False)
    update_available = False
    if got_image:
        if check_for_updates:
            update_available = artifice_core.start_rampart.check_for_image_updates(docker_client, image)
        if update_available:
            image_status = translator(f'Update available for {name} image')
            pull_text = translator(f'Install update to {name} image')
            text_color = FAIL_TEXT_COLOUR
        else:
            image_status = translator(f'{name} image installed')
            pull_text = translator(f'Check for updates to {name} image')
            text_color = PASS_TEXT_COLOUR
    else:
        image_status = translator(f'{name} image not installed')
        pull_text = translator(f'Install {name} image')
        text_color = FAIL_TEXT_COLOUR

    return got_image, docker_client, update_available, image_status, pull_text, text_color

def install_image(name, image_repo, window, font, language, translate_scheme, client):
    client = docker.from_env()
    install_popup = create_install_popup(name, font)
    old_images = client.images.list('polionanopore/piranha')

    #remove any old tags
    for image in old_images:
        for tag in image.tags:
            client.images.remove(tag)
    image_tag = f'{image_repo}:latest'
    print(image_tag)
    #client.images.remove
    
    try:
        client.images.pull(image_tag)
    except docker.credentials.errors.InitializationError as err:
        update_log(err)
        update_log('Credential initaliasion error (likely MacOS), attempting fix...')
        create_alt_docker_config()
        docker_data_dir = artifice_core.consts.get_datadir() / 'docker'
        docker_data_dir = str(docker_data_dir).replace(' ', '\\ ')
        update_log(f'pulling {name} image using alternate config')

        command = ["/usr/local/bin/docker", "--config",docker_data_dir,"pull", image_tag]
        update_log(command)
        #os.system(command)
        ret = subprocess.run(command, shell=False, text=True, capture_output=True)
        update_log(ret.stdout)
        update_log(ret.stderr)

    try:
        client.images.get(image_tag)
    except:
        err_text = translate_text('docker was unable to pull image',language,translate_scheme)
        raise Exception(err_text)

    image_status = f'{name} image installed'
    image_status = translate_text(image_status,language,translate_scheme)
    pull_text = f'Check for updates to {name} image'
    pull_text = translate_text(pull_text,language,translate_scheme)
    text_color = PASS_TEXT_COLOUR
    window[f'-{name} INSTALL-'].update(text=pull_text, visible=False)
    window[f'-{name} IMAGE STATUS-'].update(image_status, text_color=text_color)
    install_popup.close()
        

def run_startup_window(window, font=None, scale=1, version='ARTIFICE'):
    #client = docker.from_env(credstore_env={'credStore':'desktop'})
    #print(client.configs())
    client = docker.from_env()

    config = artifice_core.consts.retrieve_config()
    
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    
    translate_scheme = get_translate_scheme()


    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == '-EXIT-':
            window.close()
            break
            return

        elif event == '-DOCKER INSTALL-':
            try:
                open_new_tab('https://docs.docker.com/get-docker/')
            except Exception as err:
                error_popup(err, font)

        elif event == '-RAMPART INSTALL-':
            try:
                install_image('RAMPART',artifice_core.consts.RAMPART_IMAGE,window,font,language,translate_scheme,client)
                client = docker.from_env()
            except Exception as err:
                error_popup(err, font)

        elif event == '-PIRANHA INSTALL-':
            try:
                install_image('PIRANHA',artifice_core.consts.PIRANHA_IMAGE,window,font,language, translate_scheme,client)
                client = docker.from_env()
            except Exception as err:
                error_popup(err, font)

        elif event == '-OPTIONS-':
            try:
                options_window = create_options_window(font=font, scale=scale, version=version)
                run_options_window(options_window, font)
                options_window.close()
                window = create_startup_window(window=window,version=version,scale=scale,font=font)

                config = artifice_core.consts.retrieve_config()
                try:
                    language = config['LANGUAGE']
                except:
                    language = 'English'
            except Exception as err:
                """
                update_log(traceback.format_exc())
                sg.popup_error(err)
                """
                error_popup(err, font)


        elif event == '-LAUNCH-':
            window.close()
            return False
