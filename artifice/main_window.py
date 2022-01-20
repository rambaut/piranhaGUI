import PySimpleGUI as sg
from os import listdir, mkdir, remove, getcwd
import os.path
import requests
import json
from webbrowser import open_new_tab
from shutil import rmtree, move
from datetime import datetime
from time import sleep

import selection_window
import parse_columns_window
import start_rampart
import view_barcodes_window

RAMPART_PORT_1 = 1100
RAMPART_PORT_2 = 1200
ARCHIVED_RUNS = 'archived_runs'
RUNS_DIR = 'runs'
DOCKER_IMAGE = 'artifice_polio_rampart'
FONT = 'Arial'
#BACKGROUND_COLOR = "#072429"


def make_theme():
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

#defines the layout of the window
def setup_layout(theme='Dark', font = None):
    sg.theme(theme)
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
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-RUN NAME-',),
        ],
        [
        sg.Text('Date Created:',size=(13,1)),
        sg.Text('', size=(25,1), enable_events=True,expand_y=False, key='-DATE-',),
        ],
        [
        sg.Text('Description:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-RUN DESCRIPTION-',),
        ],
        [
        sg.Text('Samples:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        sg.Button(button_text='View',key='-VIEW SAMPLES-'),
        ],
        [
        sg.Text('MinKnow run:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
        sg.FolderBrowse(),
        ],
        [
        sg.Button(button_text='Delete',key='-DELETE RUN-'),
        sg.Button(button_text='Archive',key='-ARCHIVE/UNARCHIVE-'),
        ],
        [
        sg.Push(),
        sg.Button(button_text='RAMPART >', key='-TO RAMPART-'),
        ],
    ]
    try:
        r = requests.get(f'http://localhost:{RAMPART_PORT_1}')
        if r.status_code == 200:
            rampart_running = True
            rampart_button_text = 'Stop RAMPART'
        else:
            rampart_running = False
    except:
        rampart_running = False

    rampart_running = check_rampart_running()
    if rampart_running:
        rampart_button_text = 'Stop RAMPART'
        rampart_status = 'RAMPART is running'
    else:
        rampart_button_text = 'Start RAMPART'
        rampart_status = 'RAMPART is not running'




    rampart_tab = [
    [sg.Button(button_text='View Barcodes',key='-VIEW BARCODES-'),],
    [sg.Text(rampart_status, key='-RAMPART STATUS-'),],
    [
    sg.Button(button_text=rampart_button_text,key='-START/STOP RAMPART-'),
    sg.Button(button_text='View RAMPART', visible=rampart_running,key='-VIEW RAMPART-'),
    ],
    [
    sg.VPush()
    ],
    [
    sg.Button(button_text='< Info', key='-TO INFO-'),
    sg.Push(),
    ],
    ]

    tabs_column = [
        [
        sg.TabGroup([[sg.Tab('Info',run_info_tab,key='-RUN INFO TAB-'),sg.Tab('RAMPART',rampart_tab,key='-RAMPART TAB-')]])
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
        sg.Frame('',[[sg.Image(source = processed_image), sg.Text("ARTIFICE", font = (FONT,30), background_color = frame_bg)]], background_color = frame_bg)
        ],
        [
        sg.pin(sg.Column(select_run_column, element_justification = 'center', key='-SELECT RUN COLUMN-')),
        sg.Column(tabs_column, expand_y=True, expand_x=True,key='-TAB COLUMN-'),
        ],
    ]

    return layout, rampart_running

#retrieve the paths of directories in the run folder
def get_runs(runs_dir = RUNS_DIR, archived_json = ARCHIVED_RUNS, hide_archived = True):
    paths = listdir('./'+runs_dir)
    runs_set = set()
    for path in paths:
        if os.path.isdir('./'+runs_dir+'/'+path):
            runs_set.add(path)

    if hide_archived:
        archived_filepath = './'+runs_dir+'/'+archived_json+'.json'

        with open(archived_filepath,'r') as file:
            archived_runs_dict = json.loads(file.read())

        archived_runs = archived_runs_dict['archived_runs']
        for run in archived_runs:
            try:
                runs_set.remove(run)
            except:
                continue

    runs = list(runs_set)

    return runs

def check_rampart_running():
    try:
        r = requests.get(f'http://localhost:{RAMPART_PORT_1}')
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False

#creates a directory containing run info json
def save_run(run_info, title = None, overwrite = False, iter = 0, runs_dir = RUNS_DIR):
    samples = run_info['samples']
    if title == None or title == '':
        title = samples.split('/')[-1].split('.')[0]

    original_title = title

    if iter > 0:
        title = title+'('+str(iter)+')'

    filepath = './'+runs_dir+'/'+title+'/run_info.json'

    if overwrite == False:
        if os.path.isfile(filepath):
            return save_run(run_info,title=original_title,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    if not os.path.isdir('./'+runs_dir+'/'+title):
        mkdir('./'+runs_dir+'/'+title)

    for key, value in run_info.items():
        if type(run_info[key]) == str:
            run_info[key] = value.strip()

    run_info['title'] = title

    with open(filepath, 'w') as file:
        json.dump(run_info, file)

    return title

def create_run():
    window = selection_window.create_select_window(font=font)
    selections = selection_window.run_select_window(window)

    if selections == None:
        return None

    samples, basecalledPath, has_headers = selections

    window, column_headers = parse_columns_window.create_parse_window(samples, font=font,has_headers=has_headers)
    samples_barcodes_indices = parse_columns_window.run_parse_window(window, samples, column_headers)

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
    view_barcodes_window.save_barcodes(run_info)

    return title

def load_run(window, title, runs_dir = RUNS_DIR):
    filepath = './'+runs_dir+'/'+title+'/run_info.json'

    with open(filepath,'r') as file:
        run_info = json.loads(file.read())
        try:
            window['-DATE-'].update(run_info['date'])
        except:
            window['-DATE-'].update('')

        try:
            window['-RUN NAME-'].update(run_info['title'])
        except:
            window['-RUN NAME-'].update('')

        try:
            window['-RUN DESCRIPTION-'].update(run_info['description'])
        except:
            window['-RUN DESCRIPTION-'].update('')

        try:
            window['-SAMPLES-'].update(run_info['samples'])
        except:
            window['-SAMPLES-'].update('')

        try:
            window['-MINKNOW-'].update(run_info['basecalledPath'])
        except:
            window['-MINKNOW-'].update('')

    if 'archived' not in run_info:
        run_info['archived'] = False

    if run_info['archived'] == True:
        window['-ARCHIVE/UNARCHIVE-'].update(text='Unarchive')
    else:
        window['-ARCHIVE/UNARCHIVE-'].update(text='Archive')


    return run_info

def get_run_info(values, run_info):
    run_info['title'] = values['-RUN NAME-'].strip()
    run_info['description'] = values['-RUN DESCRIPTION-'].strip()
    run_info['samples'] = values['-SAMPLES-'].strip()
    run_info['basecalledPath'] = values['-MINKNOW-'].strip()

    return run_info

def delete_run(title, window, clear_selected = True, runs_dir = RUNS_DIR):
    filepath = './'+runs_dir+'/'+title

    if os.path.isdir(filepath):
        rmtree(filepath)

    if clear_selected:
        clear_selected_run(window)

def clear_selected_run(window):
    window['-DATE-'].update('')
    window['-RUN NAME-'].update('')
    window['-RUN DESCRIPTION-'].update('')
    window['-SAMPLES-'].update('')
    window['-MINKNOW-'].update('')

    return {}

def update_run_list(window, run_info, run_to_select = '', hide_archived = True):
    runs = get_runs(hide_archived=hide_archived)
    window['-RUN LIST-'].update(values=runs)

    if run_to_select == '':
        if 'title' in run_info:
            run_to_select = run_info['title']
        else:
            return run_info

    run_info = {}
    for i in range(len(runs)):
        if runs[i] == run_to_select:
            window['-RUN LIST-'].update(set_to_index=i)
            run_info = load_run(window, run_to_select)

    if run_info == {}:
        run_info = clear_selected_run(window)

    return run_info

def launch_rampart(run_info, client, firstPort = 1100, secondPort = 1200, runs_dir = RUNS_DIR, font = None, container = None):
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')

    basecalled_path = run_info['basecalledPath']

    config_path = './'+runs_dir+'/'+run_info['title']+'/run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dump(run_configuration, file)
        #file.write(config_json)

    view_barcodes_window.check_barcodes(run_info,font=font)

    run_path = getcwd()+'/'+runs_dir+'/'+run_info['title']
    start_rampart.start_rampart(run_path, basecalled_path, client, DOCKER_IMAGE, firstPort = firstPort, secondPort = secondPort, container=container)

    iter = 0
    while True:
        sleep(0.1)
        iter += 1
        if iter > 100:
            raise Exception('Something went wrong launching RAMPART')
        try:
            rampart_running = check_rampart_running()
            if rampart_running:
                return True
        except:
            pass

def create_main_window(theme = 'Artifice', font = None, window = None):
    make_theme()
    layout, rampart_running = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    new_window['-RUN NAME-'].bind("<FocusOut>", "FocusOut")
    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-RUN DESCRIPTION-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")

    return new_window, rampart_running

def save_changes(values, run_info, rename = False, overwrite = True, hide_archived = True):
    title = run_info['title']
    run_info = get_run_info(values, run_info)

    if rename:
        title = run_info['title']
    else:
        run_info['title'] = title

    title = save_run(run_info, title=title, overwrite=overwrite)
    run_info = update_run_list(window, run_info, hide_archived=hide_archived)

    return run_info

def rename_run(values, run_info, window, hide_archived = True):
    previous_run_title = values['-RUN LIST-'][0]
    run_info = get_run_info(values, run_info)
    if run_info['title'] != previous_run_title:
        run_info = save_changes(values, run_info, rename=True, overwrite=False, hide_archived=hide_archived)
        edit_archive(run_info['title'], archive=run_info['archived'])
        edit_archive(previous_run_title, archive=False)
        delete_run(previous_run_title, window, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)

def edit_archive(title, runs_dir = RUNS_DIR, archived_runs = ARCHIVED_RUNS, clear_selected = True, archive = True):
    archived_filepath = './'+runs_dir+'/'+archived_runs+'.json'

    with open(archived_filepath,'r') as file:
        archived_runs_dict = json.loads(file.read())

    if archive:
        archived_runs_dict['archived_runs'].append(title)
    else:
        try:
            archived_runs_dict['archived_runs'].remove(title)
        except:
            pass

    with open(archived_filepath,'w') as file:
        archived_json = json.dump(archived_runs_dict, file)

    if clear_selected:
        clear_selected_run(window)

def archive_button(run_info, window, values, hide_archived):
    if 'archived' not in run_info:
        run_info['archived'] = False

    if run_info['archived'] == True:
        run_info['archived'] = False
        run_info = save_changes(values, run_info, hide_archived=hide_archived)
        edit_archive(run_info['title'], archive=False, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)

    else:
        run_info['archived'] = True
        run_info = save_changes(values, run_info, hide_archived=hide_archived)
        edit_archive(run_info['title'], archive=True, clear_selected=True)
        if hide_archived:
            run_info = {}
            run_info = update_run_list(window, run_info, hide_archived=hide_archived)
        else:
            run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)

    return run_info

def run_main_window(window, font = None, rampart_running = False):
    runlist_visible = True
    hide_archived = True
    run_info = {}
    selected_run_title = ''
    docker_client = None
    rampart_container = None

    got_image, docker_client = start_rampart.check_for_image(docker_client, DOCKER_IMAGE, font=font)

    if not got_image:
        window.close()
        return None

    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if rampart_running:
                chk_stop = sg.popup_yes_no('Do you wish to stop RAMPART before closing', font=font)

                if chk_stop == 'Yes':
                    window.close()
                    start_rampart.stop_rampart(client=docker_client, container=rampart_container)
            window.close()
            break

        elif event == '-RUN LIST-':
            try:
                selected_run_title = values['-RUN LIST-'][0]
                run_info = load_run(window, selected_run_title)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-NEW RUN-':
            try:
                selected_run_title = create_run()
                if selected_run_title == None:
                    continue

                run_info = update_run_list(window, run_info, run_to_select=selected_run_title, hide_archived=hide_archived)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-SHOW/HIDE ARCHIVED-':
            try:
                if hide_archived:
                    hide_archived = False
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Hide Archived Runs')
                else:
                    hide_archived = True
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Show All Runs')
            except Exception as err:
                sg.popup_error(err)

        elif event == '-VIEW SAMPLES-':
            if 'title' in run_info:
                if 'samples_column' in run_info:
                    samples_column = run_info['samples_column']
                else:
                    samples_column = None

                if 'barcodes_column' in run_info:
                    barcodes_column = run_info['barcodes_column']
                else:
                    barcodes_column = None

                try:
                    samples = values['-SAMPLES-']
                    parse_window, column_headers = parse_columns_window.create_parse_window(samples, font=font, theme=TH samples_column=samples_column, barcodes_column=barcodes_column)
                    samples_barcodes_indices = parse_columns_window.run_parse_window(parse_window,samples,column_headers)

                    if samples_barcodes_indices != None:
                        samples_column, barcodes_column = samples_barcodes_indices
                        run_info['samples'] = samples
                        run_info['barcodes_column'] = barcodes_column
                        run_info['samples_column']  = samples_column
                        view_barcodes_window.save_barcodes(run_info)

                    selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
                except Exception as err:
                    sg.popup_error(err)

        elif event == '-DELETE RUN-':
            if 'title' in run_info:
                try:
                    user_confirm = sg.popup_ok_cancel('Are you sure you want to delete this run?',font=font)
                    if user_confirm != 'OK':
                        continue
                    selected_run_title = values['-RUN LIST-'][0]
                    delete_run(selected_run_title, window)
                    run_info = {}
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived)
                except Exception as err:
                    sg.popup_error(err)

        elif event == '-ARCHIVE/UNARCHIVE-':
            if 'title' in run_info:
                try:
                    run_info = archive_button(run_info, window, values, hide_archived)
                except Exception as err:
                    sg.popup_error(err)

        elif event == '-SHOW/HIDE RUNLIST-':
            if runlist_visible:
                window['-SELECT RUN COLUMN-'].update(visible=False)
                window['-SHOW/HIDE RUNLIST-'].update(text='Show Runs')
                runlist_visible = False
            else:
                window['-SELECT RUN COLUMN-'].update(visible=True)
                window['-SHOW/HIDE RUNLIST-'].update(text='Hide Runs')
                runlist_visible = True

        elif event == '-RUN NAME-FocusOut':
            try:
                if 'title' in run_info:
                    rename_run(values, run_info, window, hide_archived=hide_archived)
                else:
                    clear_selected_run(window)
            except Exception as err:
                sg.popup_error(err)


        elif event in {'-RUN DESCRIPTION-FocusOut','-SAMPLES-FocusOut','-MINKNOW-FocusOut'}:
            try:
                if 'title' in run_info:
                    run_info = save_changes(values, run_info, hide_archived=hide_archived)
                else:
                    clear_selected_run(window)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-VIEW BARCODES-':
            try:
                view_barcodes_window.check_barcodes(run_info, font=font)

                barcodes = './'+RUNS_DIR+'/'+run_info['title']+'/barcodes.csv'
                barcodes_window, column_headers = view_barcodes_window.create_barcodes_window(barcodes,font=font)
                view_barcodes_window.run_barcodes_window(barcodes_window,barcodes,column_headers)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-START/STOP RAMPART-':
            try:
                if rampart_running:
                    rampart_running = False
                    start_rampart.stop_rampart(client=docker_client, container=rampart_container)
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is not running')
                else:
                    rampart_running = launch_rampart(run_info, docker_client, firstPort=RAMPART_PORT_1, secondPort=RAMPART_PORT_2, font=font, container=rampart_container)
                    if rampart_running:
                        window['-VIEW RAMPART-'].update(visible=True)
                        window['-START/STOP RAMPART-'].update(text='Stop RAMPART')
                        window['-RAMPART STATUS-'].update('RAMPART is running')
            except Exception as err:
                sg.popup_error(err)

        elif event == '-TO RAMPART-':
            window['-RAMPART TAB-'].select()

        elif event == '-TO INFO-':
            window['-RUN INFO TAB-'].select()

        elif event == '-VIEW RAMPART-':
            address = 'http://localhost:'+str(RAMPART_PORT_1)
            open_new_tab(address)

    window.close()


if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
