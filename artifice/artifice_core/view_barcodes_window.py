import PySimpleGUI as sg
import os.path
import csv
import traceback
from artifice_core.window_functions import get_translate_scheme, translate_text
import artifice_core.window_functions

import artifice_core.parse_columns_window
import artifice_core.consts
from artifice_core.update_log import log_event, update_log

def setup_panel(translator, samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme("PANEL")

    button_size=(72, 18)

    samples_list, column_headers = artifice_core.parse_columns_window.samples_to_list(samples, has_headers=has_headers)

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
            sg.Sizer(h_pixels=500)
            ],
            ],
        )],
    ]
    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

    return panel, column_headers

def make_barcodes_list(run_info):
    if 'samples_column' in run_info:
        samples_column = run_info['samples_column']
    else:
        samples_column = 0

    if 'barcodes_column' in run_info:
        barcodes_column = run_info['barcodes_column']
    else:
        barcodes_column = 1

    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')

    samples_list = artifice_core.parse_columns_window.samples_to_list(run_info['samples'], has_headers=False)[0]
    barcodes_list = []
    for row in samples_list:
        barcodes_list.append([row[int(samples_column)], row[int(barcodes_column)]])

    return barcodes_list

# save a barcode file based on given samples file and selected columns
def save_barcodes(run_info):
    barcodes_list = make_barcodes_list(run_info)
    title = run_info['title']
    update_log(f'saving barcodes file for run: "{title}"')
    
    # make sure run dir exists
    if not os.path.exists(artifice_core.consts.RUNS_DIR / title):
         os.mkdir(artifice_core.consts.RUNS_DIR / title)

    with open(artifice_core.consts.RUNS_DIR / title / 'barcodes.csv', 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for row in barcodes_list:
            csvwriter.writerow(row)

# checks if the sample file used to make barcodes file has been edited  since barcode file created
def check_barcodes(run_info, font = None):
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')

    title = run_info['title']
    update_log(f'checking barcodes for run: "{title}" still match chosen samples...')

    barcodes_file = artifice_core.consts.RUNS_DIR / title / 'barcodes.csv'
    if os.path.isfile(barcodes_file):
        new_barcodes = make_barcodes_list(run_info)
        old_barcodes = artifice_core.parse_columns_window.samples_to_list(barcodes_file, has_headers=False)[0]
        new_barcodes.sort()
        old_barcodes.sort()

        if old_barcodes != new_barcodes:
            sample_modified = True
        else:
            sample_modified = False

        if sample_modified:
            update_log('barcodes and samples do not match')
            overwrite_barcode = sg.popup_yes_no(
                'Samples file appears to have been edited since it was selected. Do you want to remake the barcodes file with the modified samples?',
                font=font
            )
            if overwrite_barcode == "Yes":
                update_log('user chose to remake barcodes')
                save_barcodes(run_info)
            else:
                update_log('user chose to keep barcodes as they are')
        else:
            update_log('barcodes and samples match')
    else:
        update_log(f'missing barcodes file, creating it now')
        save_barcodes(run_info)

    return False

def create_barcodes_window(samples, theme = 'Artifice', font = None, window = None, samples_column = 0, barcodes_column = 1, has_headers = True):
    update_log('creating view barcodes window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    panel, column_headers = setup_panel(translator, font = font)

    content = artifice_core.window_functions.setup_content(panel, translator, button_text='Close', button_key='-BARCODES OK-')

    layout = artifice_core.window_functions.setup_header_footer(content)

    new_window = sg.Window('Artifice', layout, font=font, resizable=True, margins=(0,0), element_padding=(0,0))
    if window != None:
        window.close()

    return new_window, column_headers

def run_barcodes_window(window, samples, column_headers):
    while True:
        event, values = window.read()
        if event != None:
            log_event(f'{event} [view barcodes window]')

        if event in {'Exit', '-BARCODES OK-'} or event == sg.WIN_CLOSED:
            window.close()
            break

if __name__ == '__main__':
    samples = '/home/corey/Desktop/P_GUI_test/piranha/artifice/test_files/barcodes.csv'
    #samples_headers = ["sample", "barcode"]
    window, column_headers = create_barcodes_window(samples, has_headers=True)
    run_barcodes_window(window, samples, column_headers)

    window.close()
