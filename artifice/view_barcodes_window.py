import PySimpleGUI as sg
import os.path
import csv

import parse_columns_window
import main_window

def setup_barcodes_layout(samples, theme = 'Dark', samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme(theme)

    samples_list, column_headers = parse_columns_window.samples_to_list(samples, has_headers=has_headers)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    layout = [
        [sg.Column([
            [
            sg.Table(
            values=samples_list, headings=column_headers, visible_column_map=visible_column_map, key='-TABLE-',
            expand_x=True,expand_y=True,num_rows=30,vertical_scroll_only=False,col_widths=[20,10]#def_col_width=50,max_col_width=30
            ),
            ],
            [
            sg.Button(button_text='Ok',key='-BARCODES OK-', size=(10,1)),
            ],
            [
            sg.Sizer(h_pixels=500)
            ],
            ],
        )],
    ]

    return layout, column_headers

def make_barcodes_list(run_info):
    if 'samples_column' in run_info:
        samples_column = run_info['samples_column']
    else:
        samples_column = 0

    if 'barcodes_column' in run_info:
        barcodes_column = run_info['barcodes_column']
    else:
        barcodes_column = 1

    samples_list = parse_columns_window.samples_to_list(run_info['samples'], has_headers=False)[0]
    barcodes_list = []
    print(samples_list)
    for row in samples_list:
        barcodes_list.append([row[int(samples_column)], row[int(barcodes_column)]])

    return barcodes_list

def save_barcodes(run_info):
    barcodes_list = make_barcodes_list(run_info)
    print(barcodes_list)

    with open('runs/'+run_info['title']+'/barcodes.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)

def check_barcodes(run_info):
    barcodes_file = '.'+main_window.RUNS_DIR+'/'+run_info['title']+'/barcodes.csv'
    if os.path.isfile(barcodes_file):
        new_barcodes = make_barcodes_list(run_info)
        old_barcodes = parse_columns_window.samples_to_list(barcodes_file, has_headers=False)
        #return False
        #if old_barcodes != new_barcodes:
    else:
        save_barcodes(run_info)



def create_barcodes_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None, samples_column = 0, barcodes_column = 1, has_headers = True):
    layout, column_headers = setup_barcodes_layout(samples, samples_column=samples_column, barcodes_column=barcodes_column, has_headers=has_headers)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)
    if window != None:
        window.close()

    return new_window, column_headers


def run_barcodes_window(window, samples, column_headers):
    while True:
        event, values = window.read()
        if event in {'Exit', '-BARCODES OK-'} or event == sg.WIN_CLOSED:
            window.close()
            break

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window, column_headers = create_barcodes_window(samples, has_headers=True)
    print('?')
    run_barcodes_window(window, samples, column_headers)

    window.close()
