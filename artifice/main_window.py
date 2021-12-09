import PySimpleGUI as sg
from os import listdir, remove
import os.path
import json
import selection_window
import parse_columns_window
import csv
from webbrowser import open_new_tab
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
        sg.Button(button_text='view',key='-VIEW SAMPLES-'),
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
    runs = listdir(dir)
    for i in range(len(runs)):
        runs[i] = runs[i][:-5]

    return runs

def save_run(run_info, name = None, overwrite = False, iter = 0):
    samples = run_info['samples']
    if name == None or name == '':
        name = samples.split('/')[-1].split('.')[0]

    original_name = name

    if iter > 0:
        name = name+'('+str(iter)+')'

    filepath = './runs/'+name+'.json'

    if overwrite == False:
        if os.path.isfile(filepath):
            return save_run(run_info,name=original_name,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    run_info['name'] = name

    with open(filepath, 'w') as file:
        run_json = json.dumps(run_info)
        file.write(run_json)

    return name


def create_run():
    window = selection_window.create_select_window()
    selections = selection_window.run_select_window(window)

    if selections == None:
        return None

    samples, MinKnow = selections

    window, samples_headers = parse_columns_window.create_parse_window(samples)
    samples_headers = parse_columns_window.run_parse_window(window, samples, samples_headers)

    if samples_headers == None:
        return None

    run_info = {}

    run_info['samples'] = samples
    run_info['samples_headers'] = samples_headers
    run_info['MinKnow'] = MinKnow

    name = save_run(run_info)

    return name


def load_run(window, name):
    filepath = './runs/'+name+'.json'
    with open(filepath,'r') as file:
        run_info = json.loads(file.read())
        try:
            window['-DATE-'].update(run_info['date'])
        except:
            window['-DATE-'].update('')

        try:
            window['-RUN NAME-'].update(run_info['name'])
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
            window['-MINKNOW-'].update(run_info['MinKnow'])
        except:
            window['-MINKNOW-'].update('')

    return run_info

def get_run_info(values, run_info):

    run_info['date'] = values['-DATE-']
    run_info['name'] = values['-RUN NAME-']
    run_info['description'] = values['-RUN DESCRIPTION-']
    run_info['samples'] = values['-SAMPLES-']
    run_info['MinKnow'] = values['-MINKNOW-']

    return run_info

def delete_run(name, window, clear_selected = True):
    filepath = './runs/'+name+'.json'

    if os.path.isfile(filepath):
        remove(filepath)

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

    if 'name' not in run_info or not len(run_info['name']) > 0:
        raise Exception('Invalid Name')

    if 'MinKnow' not in run_info or os.path.isdir(run_info['MinKnow']) == False:
        raise Exception('Invalid MinKnow')

    try:
        os.makedirs('resources/template_config')
    except:
        pass
    try:
        os.mkdir('rampart')
    except:
        pass

    json_dict['basecalledPath'] = str(run_info['MinKnow'])+'/basecalled'
    json_dict['title'] = str(run_info['name'])
    with open('resources/template_config/run_configuration.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(json_dict))

    barcodes_list = parse_columns_window.csv_to_list(run_info['barcodes'])
    with open('resources/template_config/barcodes.csv', 'w', newline='') as csvfile:
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
    filename = ''

    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            start_rampart.stop_rampart()
            break

        elif event == '-RUN LIST-':
            filename = values['-RUN LIST-'][0]
            run_info = load_run(window, filename)

        elif event == '-NEW RUN-':
            try:
                filename = create_run()
                if filename == None:
                    continue

                run_info = update_run_list(window, run_info, run_to_select=filename)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-VIEW SAMPLES-':
            if 'samples_headers' in run_info:
                samples_headers = run_info['samples_headers']
            else:
                samples_headers = None

            try:
                samples = values['-SAMPLES-']
                parse_window, samples_headers = parse_columns_window.create_parse_window(samples, samples_headers=samples_headers)
                samples_headers = parse_columns_window.run_parse_window(parse_window, samples, samples_headers)
                if samples_headers != None:
                    run_info['samples_headers'] = samples_headers
                filename = save_run(run_info, name=filename, overwrite=True)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-SAVE RUN-':
            run_info = get_run_info(values, run_info)
            try:
                if 'samples_headers' in run_info:
                    samples_headers = run_info['samples_headers']
                else:
                    samples_headers = None

                name = run_info['name']
                run_info['samples_headers'] = parse_columns_window.fit_sample_headers(run_info['samples'], samples_headers)
                name = save_run(run_info, name=name, overwrite=True)
                run_info = update_run_list(window, run_info, run_to_select=name)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-DELETE RUN-':
            try:
                user_confirm = sg.popup_ok_cancel('Are you sure you want to delete this run?',font=font)
                if user_confirm != 'OK':
                    continue
                filename = values['-RUN LIST-'][0]
                delete_run(filename, window)
                run_info = {}
                run_info = update_run_list(window, run_info)
            except Exception as err:
                sg.popup_error(err)

        elif event == '-SHOW/HIDE RUNLIST-':
            if runlist_visible:
                window['-SELECT RUN COLUMN-'].update(visible=False)
                window['-SHOW/HIDE RUNLIST-'].update(text='Show Runs')
                #window['-TAB COLUMN-'].expand(expand_x=True)
                runlist_visible = False
            else:
                window['-SELECT RUN COLUMN-'].update(visible=True)
                window['-SHOW/HIDE RUNLIST-'].update(text='Hide Runs')
                runlist_visible = True

        elif event == '-START RAMPART-':
            try:
                #prepare_analysis(run_info)
                run_analysis(path = run_info['MinKnow'],firstPort=RAMPART_PORT_1, secondPort=RAMPART_PORT_2)
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
