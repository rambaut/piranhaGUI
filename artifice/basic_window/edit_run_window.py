import PySimpleGUI as sg
import traceback
import docker

import artifice_core.parse_columns_window
import artifice_core.consts
import artifice_core.start_rampart
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

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

def setup_layout(theme='Dark', font = None, version = 'ARTIFICE',):
    sg.theme(theme)
    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    is_piranhaGUI = version.startswith('piranhaGUI')

    button_size=(120,36)
    layout = [
    [
    sg.Text(translate_text('Samples:',language,translate_scheme),size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
    AltFileBrowse(button_text=translate_text('Browse',language,translate_scheme),file_types=(("CSV Files", "*.csv"),),size=button_size,font=font),
    AltButton(button_text=translate_text('View',language,translate_scheme),size=button_size,font=font,key='-VIEW SAMPLES-'),
    ],
    [
    sg.Text(translate_text('MinKnow run:',language,translate_scheme),size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
    AltFolderBrowse(button_text=translate_text('Browse',language,translate_scheme),font=font,size=button_size),
    ],
    [
    sg.Text(translate_text('Output Folder:',language,translate_scheme),visible=is_piranhaGUI, size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False,visible=is_piranhaGUI, key='-OUTDIR-',),
    AltFolderBrowse(button_text=translate_text('Browse',language,translate_scheme),font=font,visible=is_piranhaGUI,size=button_size,),
    ],
    [AltButton(button_text=translate_text('Confirm',language,translate_scheme),size=button_size,font=font,key='-CONFIRM-'),],
    ]


    return layout

def create_edit_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating main window')
    make_theme()
    layout = setup_layout(theme=theme, font=font, version=version)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
   
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled)

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")
    new_window['-OUTDIR-'].bind("<FocusOut>", "FocusOut")

    AltButton.intialise_buttons(new_window)

    return new_window

def run_edit_window(window, font = None, version = 'ARTIFICE'):
    config = artifice_core.consts.retrieve_config()
    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'
    docker_client = docker.from_env()

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath',
                    '-OUTDIR-':'outputPath'}
    try:
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], update_archive_button=False)
    except:
        pass

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

        elif event == '-VIEW SAMPLES-':
            try:
                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-', font, version=version)
                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                error_popup(err, font)
                """
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
        """
        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                if artifice_core.parse_columns_window.check_spaces(run_info['samples'], 0):
                    alt_popup_ok(translate_text('Warning: there are spaces in samples', language, translate_scheme),font=font)
                window.close()
                return run_info
            except Exception as err:
                error_popup(err, font)

    window.close()


if __name__ == '__main__':
    font = (artifice_core.consts.FONT, 18)

    window = create_main_window(font=font)
    run_main_window(window, font=font)

    window.close()
