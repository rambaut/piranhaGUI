import PySimpleGUI as sg
import os.path
import csv

def samples_to_list(filepath, has_headers = True, trim = True):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    if trim:
        for row in csv_list:
            for i in range(len(row)):
                row[i] = row[i].strip()

    if has_headers:
        column_headers = csv_list[0]
        samples_list = csv_list[1:]
    else:
        column_headers = []
        for i in range(1,len(csv_list[0])+1):
            column_headers.append(str(i))
        samples_list = csv_list

    return samples_list, column_headers

def setup_parse_layout(samples, theme = 'Dark', samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme(theme)

    samples_list, column_headers = samples_to_list(samples, has_headers=has_headers)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    layout = [
        [
        sg.Text('Choose Samples column:',size=(25,1)),
        sg.OptionMenu(column_headers, default_value=column_headers[int(samples_column)], key='-SAMPLES COLUMN-'),
        ],
        [
        sg.Text('Choose Barcodes column:',size=(25,1)),
        sg.OptionMenu(column_headers, default_value=column_headers[int(barcodes_column)], key='-BARCODES COLUMN-'),
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

    return layout, column_headers

def check_for_duplicate_entries(samples, column):
    samples_list = samples_to_list(samples)[0]
    entries = []
    for row in samples_list:
        entries.append(row[int(column)])

    print(entries)
    seen_entries = set()
    for entry in entries:
        if entry in seen_entries:
            return True
        seen_entries.add(entry)

    return False

def create_parse_window(samples, theme = 'Dark', font = ('FreeSans', 18), window = None, samples_column = 0, barcodes_column = 1, has_headers = True):

    layout, column_headers = setup_parse_layout(samples, samples_column=samples_column, barcodes_column=barcodes_column, has_headers=has_headers)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window, column_headers


def run_parse_window(window, samples, column_headers):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-SAVE-':
            try:
                samples_column = column_headers.index(values['-SAMPLES COLUMN-'])
                barcodes_column = column_headers.index(values['-BARCODES COLUMN-'])
                print('columns: '+str(samples_column)+' '+str(barcodes_column))

                if barcodes_column == samples_column:
                    raise Exception('barcodes and samples must be 2 separate columns')

                if check_for_duplicate_entries(samples, barcodes_column):
                    raise Exception('specified barcodes column contains duplicates')

                if check_for_duplicate_entries(samples, samples_column):
                    raise Exception('specified samples column contains duplicates')


                window.close()
                return samples_column, barcodes_column
            except Exception as err:
                sg.popup_error(err)


    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window, column_headers = create_parse_window(samples, has_headers=False)
    print(run_parse_window(window, samples, column_headers))

    window.close()
