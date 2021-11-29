#launches hello world GUI window
import PySimpleGUI as sg
import os
import json
import csv
from file_explorer import csv_to_list
import start_rampart
import webbrowser

RAMPART_PORT_1 = 1100
RAMPART_PORT_2 = 1200

#defines layout for the window
def setup_layout(filenames, theme='Dark'):
    sg.theme(theme)
    layout = [
        [sg.Text('Title:                 '), sg.Input(key='-TITLE INPUT-')],
        [sg.Text('Barcode File:          '), sg.Text(str(filenames[0]), key='-BARCODE-')],
        [sg.Text('Basecalled Path:       '), sg.In(size=(25,1), enable_events=True,expand_y=False, key='-BASECALLED PATH INPUT-',), sg.FolderBrowse(),],
        [sg.Text('References Label:      '), sg.Input(key='-REFERENCES INPUT-')],
        [
        sg.Button('Run Analysis', key='-RUN BUTTON-'),
        sg.Button('View Rampart', key='-RAMPART BUTTON-'),
        sg.Button('Previous File', key='-PREV BUTTON-'),
        sg.Button('Next File', key='-NEXT BUTTON-'),
        ],
    ]

    return layout

def create_config_window(filenames):
    layout = setup_layout(filenames)
    window = sg.Window(title='Config', layout = layout, margins = (80,100))

    return window

#check the user's inputs are valid then sets the configuration files for analysis run
def prepare_analysis(values, barcodes_file):
    json_dict = {}

    if not len(str(values['-TITLE INPUT-'])) > 0:
        raise Exception('Invalid title')

    if os.path.isfile(barcodes_file) == False:
        raise Exception('Invalid barcode file')

    if os.path.isdir(values['-BASECALLED PATH INPUT-']) == False:
        raise Exception('Invalid basecalled path')

    if not len(str(values['-REFERENCES INPUT-'])) > 0:
        raise Exception('Invalid reference label')

    try:
        os.makedirs('resources/template_config')
    except:
        pass
    try:
        os.mkdir('rampart')
    except:
        pass

    json_dict['basecalledPath'] = values['-BASECALLED PATH INPUT-']
    json_dict['title'] = str(values['-TITLE INPUT-'])
    json_dict['referencesLabel'] = str(values['-REFERENCES INPUT-'])
    with open('resources/template_config/run_configuration.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(json_dict))

    barcodes_list = csv_to_list(barcodes_file)
    with open('resources/template_config/barcodes.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)

#runs rampart using docker container
def run_analysis(firstPort = 1100, secondPort = 1200):
    cwd = os.getcwd()
    #run_command = 'rampart --protocol ' + str(cwd) + '/rampart'
    #os.system(run_command)
    start_rampart.start_rampart(cwd, firstPort = firstPort, secondPort = secondPort)


def run_config_window(window, filenames):
    files_index = 0
    while True:
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED:
            start_rampart.stop_rampart()
            break
        elif event == '-RUN BUTTON-':
            try:
                prepare_analysis(values, filenames[files_index])
                run_analysis(firstPort=RAMPART_PORT_1, secondPort=RAMPART_PORT_2)
            except Exception as err:
                sg.popup_error(err)
        elif event == '-RAMPART BUTTON-':
            address =  'http://localhost:'+str(RAMPART_PORT_1)
            webbrowser.open_new_tab(address)
        elif event == '-PREV BUTTON-':
            if files_index > 0:
                files_index -= 1
                window['-BARCODE-'].update(filenames[files_index])
        elif event == '-NEXT BUTTON-':
            if files_index + 1 < len(filenames):
                files_index += 1
                window['-BARCODE-'].update(filenames[files_index])


if __name__ == '__main__':
    filenames = ['test_files/test2.csv', 'test_files/barcodes.csv']
    window = create_config_window(filenames)
    run_config_window(window, filenames)


    window.close()
