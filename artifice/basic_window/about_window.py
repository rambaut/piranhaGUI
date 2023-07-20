import PySimpleGUI as sg

import artifice_core.parse_columns_window
import artifice_core.consts
import artifice_core.start_rampart
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image

def setup_header_footer_large(frame, font = None, version = 'ARTIFICE'):
    sg.theme("HEADER")
    layout = [
    [
        sg.Image(scale_image("artic-small.png", 1, (64,64)), pad=(8,2)),
        sg.Text('Powered by ARTIFICE | ARTICnetwork: http://artic.network', font=('Helvetica Neue Light', 14), pad=(8,2)),
    ],
    [
        frame
    ],
    [
        sg.Text('ARTIFICE developed by Corey Ansley, Áine O\'Toole, Rachel Colquhoun, Zoe Vance & Andrew Rambaut', font=('Helvetica Neue Light', 12), pad=(8,2)),
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
            sg.Column([[AltButton(button_text=translator('Close'),size=button_size,font=font,key='Exit')]], justification="right"),
        ],
    ]

    return sg.Frame("", [[sg.Column(layout, pad=(0, 0))]], border_width=0)


def setup_panel(translator, font = None):
    sg.theme("PANEL")

    panel = sg.Frame("", sg.Text("About text", border_width=0, relief="solid", pad=(0,16)))

    sg.theme("CONTENT")

    return panel

def create_about_window(version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating about window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    content = setup_content(translator, font)

    layout = setup_header_footer_large(content, font=font, version=version)

    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
   
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=icon_scaled, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_about_window(window, font = None, version = 'ARTIFICE'):
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

    window.close()


