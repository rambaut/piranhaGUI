import PySimpleGUI as sg
import os.path
import csv

def setup_layout(font):
    #file explorer column
    sg.theme('Dark')
    file_list_column = [
        [
            sg.Text('file folder'),
            sg.In(size=(25,1), enable_events=True, key='-FOLDER-', font=font),
            sg.FolderBrowse(font=font),
        ],
        [
            sg.Listbox(
                values=[], enable_events = True, size=(50,50), key ='-FILE LIST-', font=font
            )
        ],
    ]
    #column to view selected file
    file_viewer_column = [
        [sg.Text('Choose a file from the list on the left', key='-INSTRUCTIONS-', font=font)],
        [sg.Text(size=(70,1), key ='-TOUT-', font=font)],
        [sg.Table(values=[[]], visible_column_map=[True,True], key ='-TABLE-', font=font, expand_x=True,expand_y=True,num_rows=50)],    
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
                window['-TOUT-'].update(filename)
                window['-INSTRUCTIONS-'].update('Is this file correct?')
                window['-TABLE-'].update(csv_list)
            except:
                pass

if __name__ == '__main__':
    font = ('FreeSans', 11)
    layout = setup_layout(font)
    window = sg.Window('File Selector', layout)

    run_window(window)

    window.close()
