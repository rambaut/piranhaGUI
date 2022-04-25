import PySimpleGUI as sg
import os.path
import csv
import traceback

import artifice_core.view_barcodes_window
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme

# return a list with the samples from given csv file
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

def setup_parse_layout(samples, font = None, theme = None, samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme(theme)

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    samples_list, column_headers = samples_to_list(samples, has_headers=has_headers)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    layout = [
        [
        sg.Text(translate_text('Choose Samples column:',language,translate_scheme),size=(25,1)),
        sg.OptionMenu(column_headers, default_value=column_headers[int(samples_column)], key='-SAMPLES COLUMN-'),
        ],
        [
        sg.Text(translate_text('Choose Barcodes column:',language,translate_scheme),size=(25,1)),
        sg.OptionMenu(column_headers, default_value=column_headers[int(barcodes_column)], key='-BARCODES COLUMN-'),
        ],
        [
        AltButton(button_text=translate_text('Save',language,translate_scheme),font=font,key='-SAVE-'),
        ],
        [
        sg.Table(
        values=samples_list, headings=column_headers, visible_column_map=visible_column_map, key='-TABLE-',
        expand_x=True,expand_y=True,num_rows=25,vertical_scroll_only=False,
        ),
        ],
        #[
        #sg.Button(button_text='Save',key='-SAVE-'),
        #],
    ]

    return layout, column_headers

# returns True if there are duplicate entries in given column
def check_for_duplicate_entries(samples, column):
    samples_list = samples_to_list(samples)[0]
    entries = []
    for row in samples_list:
        entries.append(row[int(column)])

    #print(entries)
    seen_entries = set()
    for entry in entries:
        if entry in seen_entries:
            return True
        seen_entries.add(entry)

    return False

def create_parse_window(samples, theme = None, font = None, window = None, samples_column = 0, barcodes_column = 1, has_headers = True):

    layout, column_headers = setup_parse_layout(samples, font=font, theme=theme, samples_column=samples_column, barcodes_column=barcodes_column, has_headers=has_headers)
    new_window = sg.Window('Artifice', layout, font=font, resizable=True, finalize=True)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    update_log(f'displaying samples: "{samples}"')
    return new_window, column_headers

def view_samples(run_info, values, samples_key, font):
    if 'title' in run_info:
        if 'samples_column' in run_info:
            samples_column = run_info['samples_column']

            if 'barcodes_column' in run_info:
                barcodes_column = run_info['barcodes_column']
            else:
                samples_column = 0
                barcodes_column = 1
        else:
            samples_column = 0
            barcodes_column = 1

        samples = values[samples_key]
        parse_window, column_headers = create_parse_window(samples, font=font, samples_column=samples_column, barcodes_column=barcodes_column)
        samples_barcodes_indices = run_parse_window(parse_window,samples,column_headers)

        if samples_barcodes_indices != None:
            samples_column, barcodes_column = samples_barcodes_indices
            run_info['samples'] = samples
            run_info['barcodes_column'] = barcodes_column
            run_info['samples_column']  = samples_column
            artifice_core.view_barcodes_window.save_barcodes(run_info)

    return run_info

def run_parse_window(window, samples, column_headers):
    while True:
        event, values = window.read()
        if event != None:
            log_event(f'{event} [parse columns window]')

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-SAVE-':

            try:
                samples_column = column_headers.index(values['-SAMPLES COLUMN-'])
                barcodes_column = column_headers.index(values['-BARCODES COLUMN-'])
                #print('columns: '+str(samples_column)+' '+str(barcodes_column))
                update_log(f'column {samples_column} selected for samples, column {barcodes_column} selected for barcodes')

                if barcodes_column == samples_column:
                    raise Exception('barcodes and samples must be 2 separate columns')

                if check_for_duplicate_entries(samples, barcodes_column):
                    raise Exception('specified barcodes column contains duplicates')

                if check_for_duplicate_entries(samples, samples_column):
                    raise Exception('specified samples column contains duplicates')


                window.close()
                return samples_column, barcodes_column
            except Exception as err:
                error_popup(err, font)


    window.close()
    return None

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window, column_headers = create_parse_window(samples, has_headers=False)
    print(run_parse_window(window, samples, column_headers))

    window.close()
