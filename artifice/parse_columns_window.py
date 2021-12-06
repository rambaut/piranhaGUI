import PySimpleGUI as sg
import os.path
import csv

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

def setup_parse_layout(samples,theme='Dark'):
    sg.theme(theme)

    samples_list = csv_to_list(samples)

    visible_column_map = []
    header_list = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)
        header_list.append('unassigned')
    header_list[0:2] = ['sample','barcode']
    print(visible_column_map)
    print(samples_list)

    layout = [
        [
        sg.Table(values=samples_list, headings=header_list, visible_column_map=visible_column_map, key='-TABLE-', expand_x=True,expand_y=True,num_rows=30,), #select_mode='extended'),
        ],
        [
        sg.Button(button_text='Next',key='-NEXT-'),
        ],
    ]

    return layout

def create_parse_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_parse_layout(samples)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window


def run_parse_window(window, samples, MinKnow = ''):

    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-NEXT-':
            window.close()
            return samples, MinKnow



    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/test.csv'
    window = create_parse_window(samples)
    run_parse_window(window, samples)

    window.close()
