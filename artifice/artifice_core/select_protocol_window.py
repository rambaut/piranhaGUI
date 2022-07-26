from asyncio import protocols
import PySimpleGUI as sg
import traceback
from os import listdir

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

def setup_layout(theme='Dark', font = None):
    sg.theme(theme)
    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    language = config['LANGUAGE']

    protocols = ['test', 'test1']

    button_size=(120,36)

    view_protocol_column = [
        [sg.Text('test')],
        [
            sg.Listbox(
                values=protocols, enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
            )
        ],
    ]

    protocol_info_column = [
    [
    sg.Text(translate_text('Samples:',language,translate_scheme),size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
    AltFileBrowse(button_text=translate_text('Browse',language,translate_scheme),file_types=(("CSV Files", "*.csv"),),size=button_size,font=font),
    ],
    [AltButton(button_text=translate_text('Confirm',language,translate_scheme),size=button_size,font=font,key='-CONFIRM-'),],
    ]
    layout = [
        [sg.Column(view_protocol_column),
         sg.Column(protocol_info_column)],
    
    ]


    return layout

def create_protocol_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating protocol window')
    make_theme()
    layout = setup_layout(theme=theme, font=font)
    piranha_scaled = scale_image('piranha.png',scale,(64,64))
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=piranha_scaled)

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")

    AltButton.intialise_buttons(new_window)

    return new_window

def get_protocols(protocols_dir):
    paths = listdir(protocols_dir)
    runs_set = set()
    for path in paths:
        if os.path.isdir(protocols_dir / path):
            runs_set.add(path)


    runs = list(runs_set)

    return runs

def run_protocol_window(window, font = None, version = 'ARTIFICE'):
    config = artifice_core.consts.retrieve_config()
    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    element_dict = {'-SAMPLES-':'samples',}
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
   
        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                window.close()
                return 'test'
            except Exception as err:
                error_popup(err, font)

    window.close()
