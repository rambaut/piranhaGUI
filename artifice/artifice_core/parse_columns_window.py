from optparse import Option
import PySimpleGUI as sg
import os.path
import csv
import traceback
import sys

import artifice_core.consts as consts
import artifice_core.view_barcodes_window
import artifice_core.window_functions as window_functions
from artifice_core.language import translator
from artifice_core.update_log import log_event, update_log
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup

# return a list with the samples from given csv file
def samples_to_list(filepath, has_headers = True, trim = True):
    if not os.path.isfile(filepath):
        if filepath.endswith('.xls') or filepath.endswith('.xlsx'):
            raise Exception('Excel files are not supported')

    with open(filepath, newline = '') as csvfile:
        try:
            csvreader = csv.reader(csvfile)
            csv_list = list(csvreader)
        except Exception as err:
            raise Exception('Invalid CSV file')
        
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

def setup_panel(samples, samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme('PANEL')

    samples_list, column_headers = samples_to_list(samples, has_headers=has_headers)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)
    
    if sys.platform.startswith("darwin"): #on MacOS
        option_menu_text_color = '#000000'
    else:
        option_menu_text_color = '#f7eacd'

    layout = [
        [
            sg.Text(translator('Choose Samples column:'),size=(25,1)),
            sg.OptionMenu(column_headers, default_value=column_headers[int(samples_column)], 
                          text_color=option_menu_text_color, key='-SAMPLES COLUMN-'),
        ],
        [
            sg.Text(translator('Choose Barcodes column:'),size=(25,1)),
            sg.OptionMenu(column_headers, default_value=column_headers[int(barcodes_column)], 
                          text_color=option_menu_text_color, key='-BARCODES COLUMN-'),
        ],
        [
            AltButton(button_text=translator('Save'),key='-SAVE-'),
        ],
        [
            sg.Table(values=samples_list, headings=column_headers, visible_column_map=visible_column_map,
                     key='-TABLE-',expand_x=True,expand_y=True,num_rows=25,vertical_scroll_only=False),
        ],
        #[
        #sg.Button(button_text='Save',key='-SAVE-'),
        #],
    ]
    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16), expand_x=True, expand_y=True)

    return panel, column_headers

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

# returns True if there are spaces in given column
def check_spaces(samples, column):
    samples_list = samples_to_list(samples)[0]
    for row in samples_list:
        if ' ' in str(row[int(column)]):
            return True



def create_parse_window(samples, window = None, samples_column = 0, barcodes_column = 1, has_headers = True, version='ARTIFICE'):

    panel, column_headers = setup_panel(samples, samples_column=samples_column, barcodes_column=barcodes_column, has_headers=has_headers)

    content = window_functions.setup_content(panel, small=True, button_text='Close', button_key='-CLOSE-')

    layout = window_functions.setup_header_footer(content, small=True)

    
    new_window = sg.Window(version, layout, resizable=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    update_log(f'displaying samples: "{samples}"')
    return new_window, column_headers

def view_samples(run_info, values, samples_key, version='ARTIFICE'):
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
        parse_window, column_headers = create_parse_window(samples, samples_column=samples_column, barcodes_column=barcodes_column, version=version)
        samples_barcodes_indices = run_parse_window(parse_window,samples,column_headers)

        if samples_barcodes_indices != None:
            samples_column, barcodes_column = samples_barcodes_indices
            run_info['samples'] = samples
            run_info['barcodes_column'] = barcodes_column
            run_info['samples_column']  = samples_column
            artifice_core.view_barcodes_window.save_barcodes(run_info)

    return run_info

def run_parse_window(window, samples, column_headers, font = None):
    while True:
        event, values = window.read()
        if event != None:
            log_event(f'{event} [parse columns window]')

        if event == 'Exit' or event == sg.WIN_CLOSED or event == '-CLOSE-':
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
