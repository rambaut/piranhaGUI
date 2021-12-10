import PySimpleGUI as sg
import os.path
import csv

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

#makes sure given samples_headers fit given samples
def fit_sample_headers(samples, samples_headers):
    samples_list = csv_to_list(samples)

    if samples_headers == None or samples_headers == []:
        samples_headers = []
        for i in range(len(samples_list[0])):
            samples_headers.append('unassigned')
        samples_headers[0:2] = ['sample','barcode']

    else:
        while len(samples_headers) < len(samples_list[0]):
            samples_headers.append('unassigned')

    del samples_headers[len(samples_list):]

    return samples_headers

def setup_parse_layout(samples,theme='Dark'):
    sg.theme(theme)

    samples_list = csv_to_list(samples)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    samples_headers = []
    for i in range(1,len(samples_list[0])+1):
        samples_headers.append(str(i))

    samples_headers = []
    for i in range(1,len(samples_list[0])+1):
        samples_headers.append(str(i))

    layout = [
        [
        sg.Text('Choose Samples column:',size=(25,1)),
        sg.OptionMenu(samples_headers,default_value='1',key='-SAMPLES COLUMN-'),
        ],
        [
        sg.Text('Choose Barcodes column:',size=(25,1)),
        sg.OptionMenu(samples_headers,default_value='2',key='-BARCODES COLUMN-'),
        ],
        [
        sg.Table(
        values=samples_list, headings=samples_headers, visible_column_map=visible_column_map, key='-TABLE-',
        expand_x=True,expand_y=True,num_rows=30,vertical_scroll_only=False,
        ),
        ],
        [
        sg.Button(button_text='Save',key='-SAVE-'),
        ],
    ]

    return layout

def create_parse_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None, samples_headers = None):

    layout = setup_parse_layout(samples)
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
                print(values['-BARCODES COLUMN-'])
                window.close()
            except Exception as err:
                sg.popup_error(err)
            return values['-SAMPLES COLUMN-'], values['-BARCODES COLUMN-']

    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window = create_parse_window(samples)
    run_parse_window(window, samples)

    window.close()
