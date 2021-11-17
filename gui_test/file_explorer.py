import PySimpleGUI as sg
import os.path
import csv

def setup_layout():
    #file explorer column
    file_list_column = [
        [
            sg.Text('file folder'),
            sg.In(size=(25,1), enable_events=True, key='-FOLDER-'),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events = True, size=(50,50), key ='-FILE LIST-'
            )
        ],
    ]
    #column to view selected file
    file_viewer_column = [
        [sg.Text('Choose a file from the list on the left', key='-INSTRUCTIONS-')],
        [sg.Text(size=(100,1), key ='-TOUT-')],
        [sg.Table(values=[[]], visible_column_map=[True,True,True,True], key ='-TABLE-')]

    ]
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(file_viewer_column)
        ]
    ]
    return layout

def get_fnames(folder):
    try:
        file_list = os.listdir(folder)
    except:
       file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith(('.csv'))
    ]
    return fnames

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list




def run_window(window):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        #Folder name was filled in, make a list of files in the folder
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            fnames = get_fnames(folder)
            window['-FILE LIST-'].update(fnames)

        elif event == '-FILE LIST-':
            try:
                filename = os.path.join(
                    values['-FOLDER-'],values['-FILE LIST-'][0]
                )
                csv_list = csv_to_list(filename)
                print(csv_list)
                window['-TOUT-'].update(filename)
                window['-INSTRUCTIONS-'].update('Is this file correct?')
                window['-TABLE-'].update(csv_list)
            except:
                pass

layout = setup_layout()
window = sg.Window('File Selector', layout)

run_window(window)

window.close()
