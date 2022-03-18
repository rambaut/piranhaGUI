import PySimpleGUI as sg
import traceback
import docker
from PIL import Image

import artifice_core.parse_columns_window
import artifice_core.consts
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
import artifice_core.start_rampart

def make_theme():
    Artifice_Theme = {'BACKGROUND': "#072429",
               'TEXT': '#f7eacd',
               'INPUT': '#1e5b67',
               'TEXT_INPUT': '#f7eacd',
               'SCROLL': '#707070',
               'BUTTON': ('#f7eacd', '#d97168'),
               'PROGRESS': ('#000000', '#000000'),
               'BORDER': 1,
               'SLIDER_DEPTH': 0,
               'PROGRESS_DEPTH': 0}

    sg.theme_add_new('Artifice', Artifice_Theme)

def setup_layout(theme='Dark', font = None):
    sg.theme(theme)


    layout = [
    [
    sg.Text('Samples:',size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
    sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
    sg.Button(button_text='View',key='-VIEW SAMPLES-'),
    ],
    [
    sg.Text('MinKnow run:',size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
    sg.FolderBrowse(),
    ],
    [
    sg.Text('Output Folder:',size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-OUTDIR-',),
    sg.FolderBrowse(),
    ],
    [sg.Button(button_text='Confirm',key='-CONFIRM-'),],
    ]


    return layout

def create_edit_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    make_theme()
    layout = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")
    new_window['-OUTDIR-'].bind("<FocusOut>", "FocusOut")

    return new_window

def run_edit_window(window, font = None):
    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'
    edit_run = True

    docker_client = docker.from_env()

    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath',
                    '-OUTDIR-':'outputPath'}
    try:
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = artifice_core.consts.RUNS_DIR, update_archive_button=False)
    except:
        pass

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            break

        elif event == '-VIEW SAMPLES-':
            try:
                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-', font)
                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event in {'-SAMPLES-FocusOut','-MINKNOW-FocusOut','-OUTDIR-FocusOut'}:
            try:
                if 'title' in run_info:
                    run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                else:
                    clear_selected_run(window)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)
                try:
                    run_info = load_run(window, run_info['title'])
                except Exception as err:
                    update_log(traceback.format_exc())
                    sg.popup_error(err)

        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                window.close()
                return run_info
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    window.close()


if __name__ == '__main__':
    font = (artifice_core.consts.FONT, 18)

    window = create_main_window(font=font)
    run_main_window(window, font=font)

    window.close()
