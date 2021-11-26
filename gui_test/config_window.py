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
        [sg.Text('Basecalled Path:       '), sg.In(size=(25,1), enable_events=True,expand_y=True, key='-BASECALLED PATH INPUT-',), sg.FolderBrowse(),],
        [sg.Text('References Label:      '), sg.Input(key='-REFERENCES INPUT-')],
        [sg.Button('Run Analysis', key='-RUN BUTTON-')],
    ]

    return layout

def create_config_window(filenames):
    layout = setup_layout(filenames)
    window = sg.Window(title='Config', layout = layout, margins = (150,300))

    return window

#check the user's inputs are valid then sets the configuration files for analhysis run
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



def run_config_window(window, filenames):

    while True:
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-RUN BUTTON-':
            try:
                prepare_analysis(values, filenames[0])
            except Exception as err:
                sg.popup_error(err)


if __name__ == '__main__':
    filenames = ['test_files/test2.csv', 'test_files/barcodes.csv']
    window = create_config_window(filenames)
    run_config_window(window, filenames)


    window.close()
