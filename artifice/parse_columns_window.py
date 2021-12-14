import PySimpleGUI as sg
import os.path
import csv

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

def setup_parse_layout(samples,theme='Dark', samples_column = 1, barcodes_column = 2 ):
    sg.theme(theme)

    samples_list = csv_to_list(samples)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    column_headers = []
    for i in range(1,len(samples_list[0])+1):
        column_headers.append(str(i))

    layout = [
        [
        sg.Text('Choose Samples column:',size=(25,1)),
        sg.OptionMenu(column_headers,default_value=samples_column,key='-SAMPLES COLUMN-'),
        ],
        [
        sg.Text('Choose Barcodes column:',size=(25,1)),
        sg.OptionMenu(column_headers,default_value=barcodes_column,key='-BARCODES COLUMN-'),
        ],
        [
        sg.Table(
        values=samples_list, headings=column_headers, visible_column_map=visible_column_map, key='-TABLE-',
        expand_x=True,expand_y=True,num_rows=30,vertical_scroll_only=False,
        ),
        ],
        [
        sg.Button(button_text='Save',key='-SAVE-'),
        ],
    ]

    return layout

def check_for_duplicate_barcodes(samples, barcodes_column):
    samples_list = csv_to_list(samples)
    barcodes = []
    for row in samples_list:
        barcodes.append(row[int(barcodes_column)-1])

    seen_barcodes = set()
    for barcode in barcodes:
        if barcode in seen_barcodes:
            return True
        seen_barcodes.add(barcode)

    return False

def create_parse_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None, samples_column = 1, barcodes_column = 2):

    layout = setup_parse_layout(samples, samples_column=samples_column, barcodes_column=barcodes_column)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window


def run_parse_window(window, samples):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-SAVE-':
            try:
                if values['-BARCODES COLUMN-'] == values['-SAMPLES COLUMN-']:
                    raise Exception('barcodes and samples must be 2 seperate columns')

                if check_for_duplicate_barcodes(samples, values['-BARCODES COLUMN-']):
                    raise Exception('specified barcodes column contains duplicates')

                window.close()
                return values['-SAMPLES COLUMN-'], values['-BARCODES COLUMN-']
            except Exception as err:
                sg.popup_error(err)


    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window = create_parse_window(samples)
    run_parse_window(window, samples)

    window.close()
