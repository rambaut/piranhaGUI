import PySimpleGUI as sg
import traceback
import docker

import artifice_core.parse_columns_window
import artifice_core.consts as consts
import artifice_core.start_rampart
import artifice_core.window_functions as window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image


def setup_panel(translator):
    sg.theme("PANEL")

    button_size=(72, 18)

    column1 = [
            [
                sg.Sizer(1,56), sg.Text(translator('Samples:'), pad=(0,12), expand_y=True),
            ],
            [
                sg.Sizer(1,56), sg.Text(translator('MinKnow run:'), pad=(0,12), expand_y=True),
            ],
            [
                sg.Sizer(1,56), sg.Text(translator('Output Folder:'), pad=(0,12), expand_y=True),
            ]]
    column2 = [
            [
                sg.Sizer(1,56),
                sg.In(size=35, enable_events=True,expand_y=True, key='-SAMPLES-',font=16, pad=(0,12), disabled_readonly_background_color='#393938', disabled_readonly_text_color='#F5F1DF',readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-SAMPLES-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFileBrowse(button_text=translator('Select'),file_types=(("CSV Files", "*.csv"),),size=button_size),
                AltButton(button_text=translator('View'),size=button_size,key='-VIEW SAMPLES-'),
            ],
            [
                sg.Sizer(1,56),
                sg.In(size=35, enable_events=True,expand_y=True, key='-MINKNOW-',font=16, pad=(0,12), disabled_readonly_background_color='#393938', disabled_readonly_text_color='#F5F1DF',readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-MINKNOW-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select'),size=button_size),
            ],
            [
                sg.Sizer(1,56),
                sg.In(size=35, enable_events=True,expand_y=True, key='-OUTDIR-',font=16, pad=(0,12), disabled_readonly_background_color='#393938', disabled_readonly_text_color='#F5F1DF',readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-OUTDIR-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select'),size=button_size,),
            ]]

    panel = sg.Frame("Sequencing Run:", [[sg.Column([
            [
                sg.Column(column1, element_justification='Right'),
                sg.Column(column2),
            ]], pad=(16,16))]], border_width=0, relief="solid", pad=(0,16))

    return panel

def create_edit_window(version = 'ARTIFICE', window = None):
    update_log('creating main window')

    panel = setup_panel(window_functions.translator)

    content = window_functions.setup_content(panel, window_functions.translator, button_text='Continue', button_key='-CONFIRM-')

    layout = window_functions.setup_header_footer(content)

    new_window = sg.Window(version, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, 
                           margins=(0,0), element_padding=(0,0))
    
    new_window.set_min_size(size=(512,320))

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")
    new_window['-OUTDIR-'].bind("<FocusOut>", "FocusOut")

    AltButton.intialise_buttons(new_window)

    return new_window

def run_edit_window(window, version = 'ARTIFICE'):
    config = consts.retrieve_config()
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
                if '-SAMPLES-' not in values:
                    error_popup("Samples not found in values")

                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-', version=version)
                selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                error_popup(err)
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
                    alt_popup_ok(translate_text('Warning: there are spaces in samples', language, translate_scheme))
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()


