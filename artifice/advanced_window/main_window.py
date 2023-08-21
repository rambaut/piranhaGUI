import PySimpleGUI as sg
from os import listdir, mkdir, remove, getcwd, rename
import os.path
import requests
import json
from shutil import rmtree, move, copytree
from datetime import datetime
import traceback
from time import sleep
import re

import artifice_core.consts as consts
import artifice_core.selection_window
import artifice_core.parse_columns_window
import artifice_core.start_rampart
import artifice_core.view_barcodes_window
from artifice_core.start_piranha import start_piranha
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, update_run_list, get_runs, save_changes
from advanced_window.infotab import infotab_event
from advanced_window.rampart_tab import rampart_tab_event

#defines the layout of the window
def setup_layout():
    sg.theme('PANEL')

    runs = get_runs()

    select_run_column = [
        [
            sg.Button(button_text='Create New Run',size=(15,2),key='-NEW RUN-'),
            sg.Push()
        ],
        [
            sg.Text('Previous Runs:')
        ],
        [
            sg.Listbox(
                values=runs, enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
            )
        ],
        [
            sg.Button(button_text='Show All Runs',key='-SHOW/HIDE ARCHIVED-'),
        ],
    ]

    run_info_tab = [
        [
        sg.Text('Name:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-RUN NAME-',),
        ],
        [
        sg.Text('Date Created:',size=(13,1)),
        sg.Text('', size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-DATE-',),
        ],
        [
        sg.Text('Description:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-RUN DESCR-',),
        ],
        [
        sg.Text('Samples:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        sg.Button(button_text='View',key='-INFOTAB-VIEW SAMPLES-'),
        ],
        [
        sg.Text('MinKnow run:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-MINKNOW-',),
        sg.FolderBrowse(),
        ],
        [
        sg.Button(button_text='Delete',key='-INFOTAB-DELETE RUN-'),
        sg.Button(button_text='Archive',key='-INFOTAB-ARCHIVE/UNARCHIVE-'),
        ],
        [
        sg.Push(),
        sg.Button(button_text='RAMPART >', key='-INFOTAB-TO RAMPART-'),
        ],
    ]

    update_log('checking if RAMPART is running...')
    rampart_running = artifice_core.start_rampart.check_rampart_running()
    if rampart_running:
        rampart_button_text = 'Stop RAMPART'
        rampart_status = 'RAMPART is running'
    else:
        rampart_button_text = 'Start RAMPART'
        rampart_status = 'RAMPART is not running'

    rampart_tab = [
    [sg.Button(button_text='View Barcodes',key='-RAMPART TAB-VIEW BARCODES-'),],
    [sg.Text(rampart_status, key='-RAMPART TAB-RAMPART STATUS-'),],
    [
    sg.Button(button_text=rampart_button_text,key='-RAMPART TAB-START/STOP RAMPART-'),
    sg.Button(button_text='View RAMPART', visible=rampart_running,key='-RAMPART TAB-VIEW RAMPART-'),
    ],
    [
    sg.VPush()
    ],
    [
    sg.Button(button_text='< Info', key='-RAMPART TAB-TO INFO-'),
    sg.Push(),
    sg.Button(button_text='PIRANHA >', key='-RAMPART TAB-TO PIRANHA-'),
    ],
    ]

    piranha_tab = [
    [sg.Text('piranha'),],
    [sg.Button(button_text='Start PIRANHA',key='-START PIRANHA-'),],
    [sg.Multiline(size=(70,20),write_only=True, key='-PIRANHA OUTPUT-'),],
    [
    sg.VPush()
    ],
    [
    sg.Button(button_text='< RAMPART', key='-TO RAMPART-'),
    sg.Push(),
    ],
    ]

    tabs_column = [
        [
        sg.TabGroup([[sg.Tab('Info',run_info_tab,key='-RUN INFO TAB-'),sg.Tab('RAMPART',rampart_tab,key='-RAMPART TAB-'),sg.Tab('PIRANHA',piranha_tab,key='-PIRANHA TAB-')]])
        ],
        [
        sg.Button(button_text='Hide Runs',key='-SHOW/HIDE RUNLIST-'),
        ],
    ]

    processed_image = './resources/a_logo.png'


    # Resize PNG file to size (300, 300)
    #image_file = './resources/logo.png'
    #size = (100, 120)
    #im = Image.open(image_file)
    #im = im.resize(size, resample=Image.BICUBIC)
    #im.save(processed_image)
    #im_bytes = im.tobytes()

    frame_bg = sg.LOOK_AND_FEEL_TABLE['Artifice']['INPUT']

    layout = [
        [
        sg.Frame('',[[sg.Image(source = processed_image), sg.Text("ARTIFICE", font = (artifice_core.consts.FONT,30), background_color = frame_bg)]], background_color = frame_bg)
        ],
        [
        sg.pin(sg.Column(select_run_column, element_justification = 'center', key='-SELECT RUN COLUMN-')),
        sg.Column(tabs_column, expand_y=True, expand_x=True,key='-TAB COLUMN-'),
        ],
    ]

    return layout, rampart_running

def create_run(font=None):
    update_log(f'creating new run')
    window = artifice_core.selection_window.create_select_window(font=font)
    selections = artifice_core.selection_window.run_select_window(window)

    if selections == None:
        return None

    samples, basecalledPath, has_headers = selections

    window, column_headers = artifice_core.parse_columns_window.create_parse_window(samples, font=font,has_headers=has_headers)
    samples_barcodes_indices = artifice_core.parse_columns_window.run_parse_window(window, samples, column_headers)

    if samples_barcodes_indices == None:
        return None

    samples_column, barcodes_column = samples_barcodes_indices

    run_info = {}

    run_info['date'] = datetime.today().strftime('%Y-%m-%d')
    run_info['samples'] = samples.strip()
    run_info['basecalledPath'] = basecalledPath.strip()
    run_info['barcodes_column'] = str(barcodes_column).strip()
    run_info['samples_column']  = str(samples_column).strip()
    run_info['has_headers'] = has_headers

    title = save_run(run_info)
    artifice_core.view_barcodes_window.save_barcodes(run_info)
    update_log(f'created run: "{title}" successfully')

    return title

def create_main_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    
    #Not been upgraded to new layout...
    layout, rampart_running = setup_layout(theme=theme)
    new_window = sg.Window('ARTIFICE', layout, resizable=False, 
                           enable_close_attempted_event=True, finalize=True, icon=consts.ICON, font=consts.DEFAULT_FONT,
                            margins=(0,0), element_padding=(0,0))


    if window != None:
        window.close()

    new_window['-INFOTAB-RUN NAME-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-RUN DESCR-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-MINKNOW-'].bind("<FocusOut>", "FocusOut")

    return new_window, rampart_running

def run_main_window(window, rampart_running = False):
    runlist_visible = True
    hide_archived = True
    run_info = {}
    selected_run_title = ''
    docker_client = None
    rampart_container = None
    piranha_container = None

    element_dict = {'-INFOTAB-DATE-':'date',
                    '-INFOTAB-RUN NAME-':'title',
                    '-INFOTAB-RUN DESCR-':'description',
                    '-INFOTAB-SAMPLES-':'samples',
                    '-INFOTAB-MINKNOW-':'basecalledPath'}

    #scale_window(window)

    docker_installed = artifice_core.start_rampart.check_for_docker()
    if not docker_installed:
        window.close()
        return None

    got_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, consts.RAMPART_IMAGE, font=consts.DEFAULT_FONT)

    if not got_image:
        window.close()
        return None

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if rampart_running:
                chk_stop = sg.popup_yes_no('Do you wish to stop RAMPART while closing', font=consts.DEFAULT_FONT)
                window.close()

                if chk_stop == 'Yes':
                    update_log('stopping RAMPART...')
                    artifice_core.start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    update_log('RAMPART stopped')
                else:
                    update_log('User chose to keep RAMPART running')
            break

        elif event.endswith('-TO RAMPART-'):
            window['-RAMPART TAB-'].select()

        elif event.endswith('-TO INFO-'):
            window['-RUN INFO TAB-'].select()

        elif event.endswith('-TO PIRANHA-'):
            window['-PIRANHA TAB-'].select()

        elif event.startswith('-INFOTAB-'):
            try:
                run_info, selected_run_title, window = infotab_event(event, run_info, selected_run_title, hide_archived, 
                                                                     element_dict, consts.DEFAULT_FONT, values, window)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event.startswith('-RAMPART TAB-'):
            try:
                run_info, docker_client, rampart_container, rampart_running, window = rampart_tab_event(event, run_info, docker_client, 
                                                                                                        rampart_container, rampart_running, 
                                                                                                        consts.DEFAULT_FONT, window)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-START PIRANHA-':
            try:
                runs_dir = artifice_core.consts.RUNS_DIR
                artifice_core.start_rampart.prepare_run(run_info,runs_dir=runs_dir)

                run_path = runs_dir+'/'+run_info['title']
                basecalled_path = run_info['basecalledPath']
                piranha_container = start_piranha(run_path, basecalled_path, docker_client, consts.PIRANHA_IMAGE, container=None)
                sleep(1)
                #remove ANSI escape codes
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                piranha_output = ansi_escape.sub('', piranha_container.logs().decode('utf-8'))

                #window['-PIRANHA OUTPUT-'].print(piranha_container.logs().decode('unicode_escape'))
                window['-PIRANHA OUTPUT-'].print(piranha_output)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-RUN LIST-':
            try:
                update_log(f'run_info: {run_info}')
                old_run_info = None
                if 'title' in run_info:
                    old_run_info = dict(run_info)

                try:
                    if not old_run_info == None:
                        save_changes(values, old_run_info, window, hide_archived=hide_archived, element_dict=element_dict)
                except Exception as err:
                    update_log(traceback.format_exc())
                    sg.popup_error(err)


                selected_run_title = values['-RUN LIST-'][0]
                #run_info = load_run(window, selected_run_title)

                run_info = update_run_list(window, {}, run_to_select=selected_run_title, hide_archived=hide_archived, 
                                           element_dict=element_dict)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-NEW RUN-':
            try:
                selected_run_title = create_run(font)
                if selected_run_title == None:
                    continue

                run_info = update_run_list(window, run_info, run_to_select=selected_run_title, hide_archived=hide_archived, 
                                           element_dict=element_dict)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-SHOW/HIDE ARCHIVED-':
            try:
                if hide_archived:
                    update_log('showing archived runs')
                    hide_archived = False
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived, element_dict=element_dict)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Hide Archived Runs')
                else:
                    update_log('hiding archived runs')
                    hide_archived = True
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived, element_dict=element_dict)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Show All Runs')
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-SHOW/HIDE RUNLIST-':
            if runlist_visible:
                update_log('hiding run list')
                window['-SELECT RUN COLUMN-'].update(visible=False)
                window['-SHOW/HIDE RUNLIST-'].update(text='Show Runs')
                runlist_visible = False
            else:
                update_log('showing run list')
                window['-SELECT RUN COLUMN-'].update(visible=True)
                window['-SHOW/HIDE RUNLIST-'].update(text='Hide Runs')
                runlist_visible = True

    window.close()

if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (artifice_core.consts.FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
