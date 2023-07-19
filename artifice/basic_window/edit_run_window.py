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

def setup_header_footer(frame, font = None, version = 'ARTIFICE'):
    sg.theme("HEADER")
    layout = [
    [
        sg.Image(scale_image("artic-small.png", 1, (32,32)), pad=(8,2)),
        sg.Text('Powered by ARTIFICE | ARTICnetwork: http://artic.network', font=('Helvetica Neue Light', 14), pad=(8,2)),
    ],
    [
        frame
    ],
    [
        sg.Text('Wellcome Trust Award 206298/Z/17/Z', font=('Helvetica Neue Light', 12), pad=(8,2)),
    ]]

    return layout

def setup_content(translator, font=None):
    sg.theme("CONTENT")

    button_size=(120,24)
    layout = [
        [ 
            sg.Column(
                [[sg.Image(scale_image("piranha.png", 1, (64,64)))]],
                pad=(8,0)
            ),
            sg.Column(
                [
                    [sg.Text("Piranha v1.4.3", font=('Helvetica Neue Thin', 32))],
                    [sg.Text("Polio Direct Detection by Nanopore Sequencing (DDNS)", font=('Helvetica Neue Light', 12))],
                    [sg.Text("analysis pipeline and reporting tool", font=('Helvetica Neue Light', 12))],             
                ]
            ),
            sg.Column(
                [[sg.Image(scale_image("poseqco_logo_cropped.png", 1, (150,68)))],
                [sg.Text("Bill & Melinda Gates Foundation OPP1171890 and OPP1207299", font=('Helvetica Neue Light', 12))]],
                element_justification="right", expand_x=True, pad=(8,0))
        ],
        # [sg.HorizontalSeparator()],
        [
            setup_panel(translator, font),
        ],
        # [sg.HorizontalSeparator()],
        [
            sg.Column([[AltButton(button_text=translator('Confirm'),size=button_size,font=font,key='-CONFIRM-')]], justification="right"),
        ],
    ]

    return sg.Frame("", [[sg.Column(layout, pad=(0, 0))]], border_width=0)


def setup_panel(translator, font = None):
    sg.theme("PANEL")

    is_piranhaGUI = True

    button_size=(96, 18)

    column1 = [
            [
                sg.Text(translator('Samples:'), pad=(0,9)),
            ],
            [
                sg.Text(translator('MinKnow run:'), pad=(0,9)),
            ],
            [
                sg.Text(translator('Output Folder:'),visible=is_piranhaGUI, pad=(0,9)),
            ]]
    column2 = [
            [
                # sg.In(size=35, enable_events=True,expand_y=False, key='-SAMPLES-',font=16, pad=(0,12), disabled_readonly_background_color=None, disabled_readonly_text_color=None,readonly=True, justification="Right"),
                sg.Text(size=35, enable_events=True,expand_y=False, key='-SAMPLES-',font=16, pad=(0,12), justification="Right"),
                AltFileBrowse(button_text=translator('Select'),file_types=(("CSV Files", "*.csv"),),size=button_size,font=font),
                AltButton(button_text=translator('View'),size=button_size,font=font,key='-VIEW SAMPLES-'),
            ],
            [
                # sg.In(size=35, enable_events=True,expand_y=False, key='-MINKNOW-',font=16, pad=(0,12)),
                sg.Text(size=35, enable_events=True,expand_y=False, key='-MINKNOW-',font=16, pad=(0,12), justification="Right"),
                AltFolderBrowse(button_text=translator('Select'),font=font,size=button_size),
            ],
            [
                # sg.In(size=35, enable_events=True,expand_y=False,visible=is_piranhaGUI, key='-OUTDIR-',font=16, pad=(0,12)),
                sg.Text(size=35, enable_events=True,expand_y=False,visible=is_piranhaGUI, key='-OUTDIR-',font=16, pad=(0,12), justification="Right", border_width=2),
                AltFolderBrowse(button_text=translator('Select'),font=font,visible=is_piranhaGUI,size=button_size,),
            ]]

    panel = sg.Frame("", [[sg.Column([
            [
                sg.Column(column1, vertical_alignment='Top', element_justification='Right', pad=(16,0)),
                sg.Column(column2, vertical_alignment='Top'),
            ]], pad=(16,16))]], border_width=0, relief="solid", pad=(0,16))

    sg.theme("CONTENT")

    return panel

def create_edit_window(version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating main window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    content = setup_content(translator, font)

    layout = setup_header_footer(content, font=font, version=version)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
   
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled, margins=(0,0), element_padding=(0,0))

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


