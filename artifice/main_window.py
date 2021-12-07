import PySimpleGUI as sg
from os import listdir, remove
import os.path
import json
import selection_window
import parse_columns_window

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
                values=runs, enable_events = True, size=(40,50), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
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
        sg.FileBrowse(),
        ],
        [
        sg.Button(button_text='Save',key='-SAVE RUN-'),
        sg.Button(button_text='Delete',key='-DELETE RUN-'),
        ],
    ]

    rampart_tab = [
    [sg.Text('Rampart',size=(12,1)),]
    ]

    tabs_column = [
        [
        sg.TabGroup([[sg.Tab('Info',run_info_tab),sg.Tab('Rampart',rampart_tab)]])
        ]
    ]

    layout = [
        [
        sg.Pane(
        [sg.Column(select_run_column),sg.Column(tabs_column)],
        show_handle=True, orientation='horizontal'
        ),
        ]
    ]

    return layout

def get_runs(dir = './runs'):
    runs = listdir(dir)
    for i in range(len(runs)):
        runs[i] = runs[i][:-5]

    return runs

def save_run(run_info, name = None, overwrite = False, iter = 0):

    if name == None:
        samples = run_info['samples']
        name = samples.split('/')[-1].split('.')[0]

    if iter > 0:
        filepath = './runs/'+name+'('+str(iter)+').json'
    else:
        filepath = './runs/'+name+'.json'

    run_info['name'] = name

    if overwrite == False:
        if os.path.isfile(filepath):
            return save_run(run_info,name=name,overwrite=overwrite,iter=iter+1)

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
    run_info = {}
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

def create_main_window(theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_layout()
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window

def run_main_window(window, font = ('FreeSans', 18)):
    run_info = {}
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        elif event == '-RUN LIST-':
            name = values['-RUN LIST-'][0]
            run_info = load_run(window, name)

        elif event == '-NEW RUN-':
            name = create_run()
            if name == None:
                continue

            run_info = update_run_list(window, run_info, run_to_select=name)

        elif event == '-VIEW SAMPLES-':
            samples_headers = run_info['samples_headers']
            samples = values['-SAMPLES-']
            parse_window, samples_headers = parse_columns_window.create_parse_window(samples, samples_headers=samples_headers)
            run_info['samples_headers'] = parse_columns_window.run_parse_window(parse_window, samples, samples_headers)

        elif event == '-SAVE RUN-':
            run_info = get_run_info(values, run_info)
            name = run_info['name']
            save_run(run_info, name=name, overwrite=True)
            run_info = update_run_list(window, run_info, run_to_select=name)

        elif event == '-DELETE RUN-':
            user_confirm = sg.popup_ok_cancel('Are you sure you want to delete this run?',font=font)
            if user_confirm != 'OK':
                continue
            delete_run(run_info['name'], window)
            run_info = {}
            run_info = update_run_list(window, run_info)


    window.close()


if __name__ == '__main__':

    window = create_main_window()
    run_main_window(window)

    window.close()
