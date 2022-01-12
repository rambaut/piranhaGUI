import PySimpleGUI as sg
from os import listdir, mkdir, remove, getcwd
import os.path
import json
import csv
from webbrowser import open_new_tab
from shutil import rmtree, move
from datetime import datetime

import selection_window
import parse_columns_window
import start_rampart


RAMPART_PORT_1 = 1100
RAMPART_PORT_2 = 1200
ARCHIVED_RUNS = 'archived_runs'
RUNS_DIR = './runs'

#defines the layout of the window
def setup_layout(theme='Dark'):
    sg.theme(theme)
    runs = get_runs()

    select_run_column = [
        [
            sg.Button(button_text='Create New Run',size=(20,3),key='-NEW RUN-'),
        ],
        [sg.Text('Previous Runs:')],
        [
            sg.Listbox(
                values=runs, enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
            )
        ]
    ]

    run_info_tab = [
        [
        sg.Text('Name:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-RUN NAME-',),
        sg.Button(button_text='Rename',key='-RENAME RUN-'),
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
        sg.Button(button_text='Archive',key='-ARCHIVE RUN-'),
        ],
        [
        sg.Push(),
        sg.Button(button_text='Rampart >', key='-TO RAMPART-'),
        ],
    ]

    rampart_tab = [
    [sg.Text('Rampart',size=(12,1)),],
    [
    sg.Button(button_text='Start Rampart',key='-START RAMPART-'),
    sg.Button(button_text='View Rampart',key='-VIEW RAMPART-'),
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
        sg.TabGroup([[sg.Tab('Info',run_info_tab,key='-RUN INFO TAB-'),sg.Tab('Rampart',rampart_tab,key='-RAMPART TAB-')]])
        ],
        [
        sg.Button(button_text='Hide Runs',key='-SHOW/HIDE RUNLIST-'),
        ],
    ]

    layout = [
        [
        sg.pin(sg.Column(select_run_column, element_justification = 'center', key='-SELECT RUN COLUMN-')),
        sg.Column(tabs_column, expand_y=True, expand_x=True, key='-TAB COLUMN-'),
        ],
    ]

    return layout

#retrieve the paths of directories in the run folder
def get_runs(dir = RUNS_DIR, archived_json = ARCHIVED_RUNS, hide_archived = True):
    paths = listdir(dir)
    runs_set = set()
    for path in paths:
        if os.path.isdir(dir+'/'+path):
            runs_set.add(path)

    if hide_archived:
        archived_filepath = './'+dir+'/'+archived_json+'.json'

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

#creates a directory containing run info json
def save_run(run_info, title = None, overwrite = False, iter = 0):
    samples = run_info['samples']
    if title == None or title == '':
        title = samples.split('/')[-1].split('.')[0]

    original_title = title

    if iter > 0:
        title = title+'('+str(iter)+')'

    filepath = './runs/'+title+'/run_info.json'

    if overwrite == False:
        if os.path.isfile(filepath):
            return save_run(run_info,title=original_title,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    if not os.path.isdir('./runs/'+title):
        mkdir('./runs/'+title)

    for key, value in run_info.items():
        run_info[key] = str(value).strip()

    run_info['title'] = title

    with open(filepath, 'w') as file:
        run_json = json.dumps(run_info)
        file.write(run_json)

    return title

def create_run():
    window = selection_window.create_select_window()
    selections = selection_window.run_select_window(window)

    if selections == None:
        return None

    samples, basecalledPath, has_headers = selections

    window, column_headers = parse_columns_window.create_parse_window(samples, has_headers=has_headers)
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
    save_barcodes(run_info)

    return title

def load_run(window, title):
    filepath = './runs/'+title+'/run_info.json'

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

    return run_info

def get_run_info(values, run_info):
    run_info['title'] = values['-RUN NAME-'].strip()
    run_info['description'] = values['-RUN DESCRIPTION-'].strip()
    run_info['samples'] = values['-SAMPLES-'].strip()
    run_info['basecalledPath'] = values['-MINKNOW-'].strip()

    return run_info

def delete_run(title, window, clear_selected = True):
    filepath = './runs/'+title

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

def update_run_list(window, run_info, run_to_select = ''):
    runs = get_runs()
    window['-RUN LIST-'].update(values=runs)

    if run_to_select == '':
        return run_info

    index = 0
    for i in range(len(runs)):
        if runs[i] == run_to_select:
            index = i

    window['-RUN LIST-'].update(set_to_index=index)
    run_info = load_run(window, run_to_select)
    return run_info

def save_barcodes(run_info):
    if 'samples_column' in run_info:
        samples_column = run_info['samples_column']
    else:
        samples_column = 0

    if 'barcodes_column' in run_info:
        barcodes_column = run_info['barcodes_column']
    else:
        barcodes_column = 1

    samples_list = parse_columns_window.samples_to_list(run_info['samples'], has_headers=run_info['has_headers'])
    barcodes_list = []

    for row in samples_list:
        barcodes_list.append([row[int(samples_column)], row[int(barcodes_column)]])

    with open('runs/'+run_info['title']+'/barcodes.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)

def launch_rampart(run_info, firstPort = 1100, secondPort = 1200):
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')

    basecalled_path = run_info['basecalledPath']

    config_path = './runs/'+run_info['title']+'/run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dumps(run_configuration)
        file.write(config_json)

    run_path = getcwd()+'/runs/'+run_info['title']
    start_rampart.start_rampart(run_path, basecalled_path, firstPort = firstPort, secondPort = secondPort)

def create_main_window(theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_layout()
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window

def save_changes(values, run_info, rename = False, overwrite = True):
    title = run_info['title']
    run_info = get_run_info(values, run_info)

    if rename:
        title = run_info['title']
    else:
        run_info['title'] = title

    title = save_run(run_info, title=title, overwrite=overwrite)
    run_info = update_run_list(window, run_info, run_to_select=title)

    return run_info

def archive_run(title, runs_dir = RUNS_DIR, archived_runs = ARCHIVED_RUNS, clear_selected = True):
    archived_filepath = './'+runs_dir+'/'+archived_runs+'.json'

    with open(archived_filepath,'r') as file:
        archived_runs_dict = json.loads(file.read())

    archived_runs_dict['archived_runs'].append(title)

    with open(archived_filepath,'w') as file:
        archived_json = json.dumps(archived_runs_dict)
        file.write(archived_json)

    if clear_selected:
        clear_selected_run(window)

def run_main_window(window, font = ('FreeSans', 18)):
    runlist_visible = True
    run_info = {}
    selected_run_title = ''

    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            start_rampart.stop_rampart()
            break

        elif event == '-RUN LIST-':
            selected_run_title = values['-RUN LIST-'][0]
            run_info = load_run(window, selected_run_title)

        elif event == '-NEW RUN-':
            try:
                selected_run_title = create_run()
                if selected_run_title == None:
                    continue

                run_info = update_run_list(window, run_info, run_to_select=selected_run_title)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-VIEW SAMPLES-':
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
                parse_window, column_headers = parse_columns_window.create_parse_window(samples, samples_column=samples_column, barcodes_column=barcodes_column)
                samples_barcodes_indices = parse_columns_window.run_parse_window(parse_window,samples,column_headers)

                if samples_barcodes_indices != None:
                    samples_column, barcodes_column = samples_barcodes_indices
                    run_info['samples'] = samples
                    run_info['barcodes_column'] = barcodes_column
                    run_info['samples_column']  = samples_column

                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-RENAME RUN-':
            try:
                previous_run_title = values['-RUN LIST-'][0]
                run_info = get_run_info(values, run_info)
                if run_info['title'] != previous_run_title:
                    run_info = save_changes(values, run_info, rename=True, overwrite=False)
                    delete_run(previous_run_title, window, clear_selected=False)
                    run_info = update_run_list(window, run_info, run_to_select=run_info['title'])
            except Exception as err:
                sg.popup_error(err)

        elif event == '-DELETE RUN-':
            try:
                user_confirm = sg.popup_ok_cancel('Are you sure you want to delete this run?',font=font)
                if user_confirm != 'OK':
                    continue
                selected_run_title = values['-RUN LIST-'][0]
                delete_run(selected_run_title, window)
                run_info = {}
                run_info = update_run_list(window, run_info)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-ARCHIVE RUN-':
            try:
                archive_run(run_info['title'])
                run_info = {}
                run_info = update_run_list(window, run_info)
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

        elif event in {'-RUN DESCRIPTION-','-SAMPLES-','-MINKNOW-'}:
            try:
                run_info = save_changes(values, run_info)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-START RAMPART-':
            try:
                launch_rampart(run_info, firstPort=RAMPART_PORT_1, secondPort=RAMPART_PORT_2)
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

    window = create_main_window()
    run_main_window(window)

    window.close()
