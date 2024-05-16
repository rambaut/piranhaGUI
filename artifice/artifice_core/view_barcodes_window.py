import PySimpleGUI as sg
import os.path
import csv

from artifice_core.language import translator
import artifice_core.window_functions as window_functions

from artifice_core.parse_columns_window import samples_to_list
import artifice_core.consts as consts
from artifice_core.update_log import log_event, update_log

def setup_panel(samples_column = 0, barcodes_column = 1, has_headers = True):
    sg.theme("PANEL")

    samples_list, column_headers = samples_to_list(samples, has_headers=has_headers)

    visible_column_map = []
    for i in range(len(samples_list[0])):
        visible_column_map.append(True)

    layout = [[
        sg.Column([[
                sg.Table(values=samples_list, headings=column_headers, visible_column_map=visible_column_map, 
                        key='-TABLE-', expand_x=True,expand_y=True,num_rows=30,vertical_scroll_only=False,
                        col_widths=[20,10]#def_col_width=50,max_col_width=30
                ),
            ],
            [
             sg.Sizer(h_pixels=500)
            ]],
        )]]
    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

    return panel, column_headers

def create_barcodes_window(samples, window = None, samples_column = 0, barcodes_column = 1, has_headers = True):
    update_log('creating view barcodes window')

    title = consts.WINDOW_TITLE

    panel, column_headers = setup_panel(samples_column, barcodes_column, has_headers)

    content = window_functions.setup_content(panel, title=title, small=True, button_text='Close', button_key='-BARCODES OK-')

    layout = window_functions.setup_header_footer(content, small=True)

    new_window = sg.Window(title, layout, resizable=True, font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))
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
