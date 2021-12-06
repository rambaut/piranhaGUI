import PySimpleGUI as sg
from os import listdir
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
                values=[runs], enable_events = True, size=(40,50), select_mode = sg.LISTBOX_SELECT_MODE_EXTENDED, key ='-RUN LIST-',
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
        sg.Button(button_text='select',key='-SELECT SAMPLES-'),
        sg.Button(button_text='view',key='-VIEW SAMPLES-'),
        ],
        [
        sg.Text('MinKnow run',size=(12,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
        sg.Button(button_text='select',key='-SELECT MINKNOW-'),
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

def create_main_window(theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_layout()
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window

def get_runs(dir = './runs'):
    runs = listdir(dir)
    for i in range(len(runs)):
        runs[i] = runs[i][:-5]

    return runs

def create_run():
    window = selection_window.create_select_window()
    samples, MinKnow = selection_window.run_select_window(window)

    return samples, MinKnow


def load_run(window, values):
    print(values['-RUN LIST-'][0])
    filepath = './runs/'+values['-RUN LIST-'][0][0]+'.json'
    with open(filepath,'r') as file:
        run_info = json.loads(file.read())
        try:
            window['-DATE-'].update(run_info['date'])
        except:
            pass
        try:
            window['-RUN NAME-'].update(run_info['name'])
        except:
            pass
        try:
            window['-RUN DESCRIPTION-'].update(run_info['description'])
        except:
            pass
        try:
            window['-SAMPLES-'].update(run_info['samples'])
        except:
            pass
        try:
            window['-MINKNOW-'].update(run_info['MinKnow'])
        except:
            pass

def run_main_window(window):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-RUN LIST-':
            load_run(window, values)
        elif event == '-NEW RUN-':
            print(create_run())



    window.close()


if __name__ == '__main__':

    window = create_main_window()
    run_main_window(window)

    window.close()
