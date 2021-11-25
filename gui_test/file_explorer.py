import PySimpleGUI as sg
import os.path
import csv

#defines the layout of the window
def setup_layout(columns = 2, theme='Dark'):
    visible_column_map = []
    for i in range(columns):
        visible_column_map.append(True)

    sg.theme(theme)

    menu_def = [
    ['&Settings',['&Change number of columns::columnskey']],
    ]

    #file explorer column
    file_list_column = [
        [
            sg.Text('file folder'),
            sg.In(size=(25,1), enable_events=True,expand_y=True, key='-FOLDER-',),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events = True, size=(50,50), select_mode = sg.LISTBOX_SELECT_MODE_EXTENDED, key ='-FILE LIST-',
            )
        ],
    ]
    #column to view selected files
    file_viewer_column = [
        [sg.Text('Choose a file from the list on the left', key='-INSTRUCTIONS-')],
        [sg.Text(size=(70,1), key ='-TOUT-')],
        [sg.Table(values=[[]], visible_column_map=visible_column_map, key ='-TABLE-', expand_x=True,expand_y=True,num_rows=50)],

        [sg.Button(button_text='<',key='-LEFT BUTTON-'),
        sg.Button(button_text='>',key='-RIGHT BUTTON-'),
        sg.Text(' No files to display yet  ',visible=True, key ='-DISPLAY INDICATOR-'),
        sg.Button(button_text='Use selected file(s)',key='-USE BUTTON-'),],
    ]

    layout = [
        [
            sg.Menu(menu_def, key = '-MENU-'),
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(file_viewer_column),
        ]
    ]
    return layout

#returns the names of all files with a particular ending in the given directory
def get_fnames(folder, file_ending='.csv'):
    try:
        file_list = os.listdir(folder)
    except:
       file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((file_ending))
    ]
    return fnames

#take the given csv file, convert to list[list[]]
def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

def display_indicator_text(window, values, pos):
    if len(values['-FILE LIST-']) > 0:
        display_text = 'Displaying file '+str(pos+1)+' out of '+str(len(values['-FILE LIST-']))
        window['-DISPLAY INDICATOR-'].update(display_text)
        window['-DISPLAY INDICATOR-'].update(visible=True)
    else:
        window['-DISPLAY INDICATOR-'].update(visible=False)

#display the selected file
def display_file(window, values, pos):
    try:
        filename = os.path.join(values['-FOLDER-'],values['-FILE LIST-'][pos])

        window['-TOUT-'].update(filename)
        window['-INSTRUCTIONS-'].update('Is this file correct?')

        csv_list = csv_to_list(filename)
        window['-TABLE-'].update(csv_list)

        display_indicator_text(window, values, pos)

    except:
        pass

#prompts the user to enter number of columns via popup, verifies input is valid and relaunches window if so
def adjust_columns(window):
    columns = sg.popup_get_text('Enter how many columns needed')

    if columns == None:
        pass
    elif columns.isnumeric():
        if int(columns) > 0:
            window = create_explorer_window(columns = int(columns), window=window)
    else:
        sg.popup_ok('Please enter a postive integer')
        window = adjust_columns(window)

    return window

#helper function to create/reset window
def create_explorer_window(columns = 2, theme = 'Dark', font = ('FreeSans', 11), window = None):

    layout = setup_layout(columns = columns, theme = theme)
    new_window = sg.Window('File Selector', layout, font=font, resizable=True)
    if window != None:
        window.close()

    return new_window

def return_filenames(values):
    filenames = []
    for i in range(len(values['-FILE LIST-'])):
        filenames.append(os.path.join(values['-FOLDER-'],values['-FILE LIST-'][i]))

    return filenames


def run_explorer_window(window):

    display_file_pos = 0

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
            while (len(values['-FILE LIST-'])-1) < display_file_pos:
                display_file_pos -= 1
            display_file(window,values,display_file_pos)

        elif event == '-RIGHT BUTTON-':
            if (len(values['-FILE LIST-'])-1) > display_file_pos:
                display_file_pos += 1
                display_file(window,values,display_file_pos)

        elif event == '-LEFT BUTTON-':
            if  display_file_pos > 0:
                display_file_pos -= 1
                display_file(window,values,display_file_pos)

        elif event == '-USE BUTTON-':
            filenames = return_filenames(values)
            window.close()
            return filenames

        elif event == 'Change number of columns::columnskey':
            window = adjust_columns(window)

    window.close()

    return None

if __name__ == '__main__':

    window = create_explorer_window()
    run_explorer_window(window)

    window.close()
