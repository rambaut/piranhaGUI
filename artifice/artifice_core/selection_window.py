import PySimpleGUI as sg
import os.path
import traceback

from artifice_core.update_log import log_event, update_log
import artifice_core.consts as consts

#Window for user to select samples csv and possibling MinKnow

def setup_selection_layout():
    sg.theme('PANEL')

    layout = [
        [
        sg.Text('Samples',size=(25,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        ],
        [
        sg.Text('MinKnow run (optional)',size=(25,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
        sg.FolderBrowse(),
        ],
        [
        sg.Checkbox('Samples file contains headers', default=True, key='-HEADERS CHECKBOX-')
        ],
        [
        sg.Button(button_text='Next',key='-NEXT-'),
        ],
    ]

    return layout

def create_select_window(window = None):
    update_log(f'opening selection window')
    layout = setup_selection_layout()
    new_window = sg.Window(consts.WINDOW_TITLE, layout, icon=consts.ICON, font=consts.DEFAULT_FONT, resizable=False)

    if window != None:
        window.close()

    return new_window

def run_select_window(window):
    while True:
        event, values = window.read()
        if event != None:
            log_event(f'{event} [selection window]')

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-NEXT-':
            try:
                samples = values['-SAMPLES-'].strip()
                MinKnow = values['-MINKNOW-'].strip()
                update_log(f'selected "{samples}" as samples file')

                if os.path.isfile(samples) == False:
                    raise Exception('Invalid samples file')

                if MinKnow != '':
                    update_log(f'selected "{MinKnow}" as sequencing data')
                    if os.path.isdir(MinKnow) == False:
                        raise Exception('Invalid path to sequencing data')
                else:
                    update_log(f'No sequencing data selected')

                window.close()
                return samples, MinKnow, values['-HEADERS CHECKBOX-']
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    window.close()
    return None


if __name__ == '__main__':

    window = create_select_window()
    run_select_window(window)

    window.close()
