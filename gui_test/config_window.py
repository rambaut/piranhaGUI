#launches hello world GUI window
import PySimpleGUI as sg
import os
import json
import csv
from file_explorer import csv_to_list

def setup_layout(filenames, theme='Dark'):
    sg.theme(theme)
    layout = [
        [sg.Text('Title:                 '), sg.Input(key='-TITLE INPUT-')],
        [sg.Text('Barcode File:          '), sg.Text(str(filenames[0]), key='-BARCODE-')],
        [sg.Text('Basecalled Path:       '), sg.In(size=(25,1), enable_events=True,expand_y=True, key='-BASECALLED PATH INPUT-',), sg.FileBrowse(),],
        [sg.Text('References Label:      '), sg.Input(key='-REFERENCES INPUT-')],
        [sg.Button('Run Analysis', key='-RUN BUTTON-')],
    ]

    return layout

def create_config_window(filenames):
    layout = setup_layout(filenames)
    window = sg.Window(title='Config', layout = layout, margins = (150,300))

    return window

def prepare_analysis(values, barcodes_file):
    json_dict = {}
    json_dict['title'] = values['-TITLE INPUT-']
    json_dict['basecalledPath'] = values['-BASECALLED PATH INPUT-']
    json_dict['referencesLabel'] = values['-REFERENCES INPUT-']

    try:
        os.makedirs('resources/template_config')
    except:
        pass

    with open('resources/template_config/run_configuration.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(json_dict))

    barcodes_list = csv_to_list(barcodes_file)

    with open('resources/template_config/barcodes.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)



def run_config_window(window, filenames):

    while True:
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-RUN BUTTON-':
            prepare_analysis(values, filenames[0])

if __name__ == '__main__':
    filenames = ['test_files/test2.csv', 'test_files/barcodes.csv']
    window = create_config_window(filenames)
    run_config_window(window, filenames)


    window.close()
