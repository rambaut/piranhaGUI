import PySimpleGUI as sg
import os.path
import csv

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

def setup_parse_layout(samples,theme='Dark', header_list = None):
    sg.theme(theme)

    samples_list = csv_to_list(samples)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    if header_list == None:
        header_list = []
        for i in range(len(samples_list[0])):
            header_list.append('unassigned')
        header_list[0:2] = ['sample','barcode']

    header_inputs = []
    for i in range(len(header_list)):
        header_inputs.append(sg.In(default_text=header_list[i],size=(15,1),enable_events=True,expand_y=False, key='-HEADER'+str(i+1)+'-',),)



    layout = [
        [
        sg.Text('change column headers:',size=(25,1)),
        ],
        header_inputs,
        [
        sg.Button(button_text='apply changes to headers',key='-CHANGE HEADERS-'),
        ],
        [
        sg.Table(values=samples_list, headings=header_list, visible_column_map=visible_column_map, key='-TABLE-', expand_x=True,expand_y=True,num_rows=30,), #select_mode='extended'),
        ],
        [
        sg.Button(button_text='Next',key='-NEXT-'),
        ],
    ]

    return layout, header_list

def create_parse_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None, header_list = None):

    layout, header_list = setup_parse_layout(samples, header_list=header_list)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window, header_list


def run_parse_window(window, samples, header_list, MinKnow = ''):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-CHANGE HEADERS-':
            for i in range(len(header_list)):
                header_list[i] = values['-HEADER'+str(i+1)+'-']
            window, header_list = create_parse_window(samples, window=window, header_list=header_list)
        elif event == '-NEXT-':
            window.close()
            return samples, MinKnow, header_list



    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/test.csv'
    window, header_list = create_parse_window(samples)
    run_parse_window(window, samples, header_list)

    window.close()
