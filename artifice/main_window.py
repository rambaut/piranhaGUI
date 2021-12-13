import PySimpleGUI as sg
from os import listdir, mkdir, remove
import os.path
import json
import selection_window
import parse_columns_window
import csv
from webbrowser import open_new_tab
from shutil import rmtree
import start_rampart


RAMPART_PORT_1 = 1100
RAMPART_PORT_2 = 1200

#defines the layout of the window
def setup_layout(theme='Dark'):
    sg.theme(theme)
    runs = get_runs()

    select_run_column = [
        [
            sg.Button(button_text='New Run',size=(39,5),key='-NEW RUN-'),
        ],
        [
            sg.Listbox(
                values=runs, enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
            )
        ]
    ]

    run_info_tab = [
        [
        sg.Text('Date',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-DATE-',),
        ],
        [
        sg.Text('Name',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-RUN NAME-',),
        ],
        [
        sg.Text('Description',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-RUN DESCRIPTION-',),
        ],
        [
        sg.Text('Samples',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        sg.Button(button_text='View',key='-VIEW SAMPLES-'),
        ],
        [
        sg.Text('MinKnow run',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
        sg.FolderBrowse(),
        ],
        [
        sg.Button(button_text='Save',key='-SAVE RUN-'),
        sg.Button(button_text='Delete',key='-DELETE RUN-'),
        ],

    ]

    rampart_tab = [
    [sg.Text('Rampart',size=(12,1)),],
    [
    sg.Button(button_text='Start Rampart',key='-START RAMPART-'),
    sg.Button(button_text='View Rampart',key='-VIEW RAMPART-'),
    ],
    ]

    tabs_column = [
        [
        sg.TabGroup([[sg.Tab('Info',run_info_tab),sg.Tab('Rampart',rampart_tab)]])
        ],
        [
        sg.Button(button_text='Hide Runs',key='-SHOW/HIDE RUNLIST-'),
        ],
    ]

    layout = [
        #[
        #sg.Pane(
        #[sg.pin(sg.Column(select_run_column, key='-SELECT RUN COLUMN-')),sg.Column(tabs_column, expand_x=True,key='-TAB COLUMN-')],
        #show_handle=True, orientation='horizontal'
        #),
        #]
        [sg.pin(sg.Column(select_run_column, key='-SELECT RUN COLUMN-')),sg.Column(tabs_column, expand_y=True, expand_x=True,key='-TAB COLUMN-')],

    ]

    return layout

def get_runs(dir = './runs'):
    paths = listdir(dir)
    runs = []
    for path in paths:
        if os.path.isdir('runs/'+path):
            runs.append(path)

    return runs

def save_run(run_info, title = None, overwrite = False, iter = 0):
    samples = run_info['samples']
    if title == None or title == '':
        title = samples.split('/')[-1].split('.')[0]

    original_title = title

    if iter > 0:
        title = title+'('+str(iter)+')'

    filepath = './runs/'+title+'/run_configuration.json'

    if overwrite == False:
        if os.path.isfile(filepath):
            return save_run(run_info,title=original_title,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    if not os.path.isdir('./runs/'+title):
        mkdir('./runs/'+title)

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

    samples, basecalledPath = selections

    window = parse_columns_window.create_parse_window(samples)
    samples_barcodes_indices = parse_columns_window.run_parse_window(window, samples)

    if samples_barcodes_indices == None:
        return None

    samples_column, barcodes_column = samples_barcodes_indices

    run_info = {}

    run_info['samples'] = samples
    run_info['basecalledPath'] = basecalledPath
    run_info['barcodes_column'] = barcodes_column
    run_info['samples_column']  = samples_column

    title = save_run(run_info)

    return title

def load_run(window, title):
    filepath = './runs/'+title+'/run_configuration.json'

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

    run_info['date'] = values['-DATE-']
    run_info['title'] = values['-RUN NAME-']
    run_info['description'] = values['-RUN DESCRIPTION-']
    run_info['samples'] = values['-SAMPLES-']
    run_info['basecalledPath'] = values['-MINKNOW-']

    return run_info

def delete_run(title, window, clear_selected = True):
    filepath = './runs/'+title

    if os.path.isdir(filepath):
        rmtree(filepath)

    if clear_selected:
        window['-DATE-'].update('')
        window['-RUN NAME-'].update('')
        window['-RUN DESCRIPTION-'].update('')
        window['-SAMPLES-'].update('')
        window['-MINKNOW-'].update('')

def update_run_list(window, run_info, run_to_select= ''):
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

def prepare_analysis(run_info):
    json_dict = {}

    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')

    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name')

    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')


    if 'samples_column' in run_info:
        samples_column = run_info['samples_column']
    else:
        samples_column = 1

    if 'barcodes_column' in run_info:
        barcodes_column = run_info['barcodes_column']
    else:
        barcodes_column = 2

    samples_list = parse_columns_window.csv_to_list(run_info['samples'])
    barcodes_list = []

    for row in samples_list:
        barcodes_list.append([row[int(samples_column)-1], row[int(barcodes_column)-1]])

    with open('runs/'+run_info['title']+'/barcodes.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)

def run_analysis(path, firstPort = 1100, secondPort = 1200):
    basecalled_dir = path + '/basecalling'
    start_rampart.start_rampart(basecalled_dir, firstPort = firstPort, secondPort = secondPort)



def create_main_window(theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_layout()
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window

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
                parse_window = parse_columns_window.create_parse_window(samples, samples_column=samples_column,barcodes_column=barcodes_column)
                samples_barcodes_indices = parse_columns_window.run_parse_window(parse_window, samples)

                if samples_barcodes_indices != None:
                    samples_column, barcodes_column = samples_barcodes_indices
                    run_info['samples'] = samples
                    run_info['barcodes_column'] = barcodes_column
                    run_info['samples_column']  = samples_column

                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-SAVE RUN-':
            run_info = get_run_info(values, run_info)
            try:
                title = run_info['title']
                title = save_run(run_info, title=title, overwrite=True)
                run_info = update_run_list(window, run_info, run_to_select=title)
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

        elif event == '-SHOW/HIDE RUNLIST-':
            if runlist_visible:
                window['-SELECT RUN COLUMN-'].update(visible=False)
                window['-SHOW/HIDE RUNLIST-'].update(text='Show Runs')
                runlist_visible = False
            else:
                window['-SELECT RUN COLUMN-'].update(visible=True)
                window['-SHOW/HIDE RUNLIST-'].update(text='Hide Runs')
                runlist_visible = True

        elif event == '-START RAMPART-':
            try:
                prepare_analysis(run_info)
                run_analysis(path = run_info['basecalledPath'],firstPort=RAMPART_PORT_1, secondPort=RAMPART_PORT_2)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-VIEW RAMPART-':
            address = 'http://localhost:'+str(RAMPART_PORT_1)
            open_new_tab(address)

    window.close()


if __name__ == '__main__':

    window = create_main_window()
    run_main_window(window)

    window.close()
