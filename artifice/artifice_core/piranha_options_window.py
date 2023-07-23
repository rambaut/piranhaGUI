import PySimpleGUI as sg
import sys

import artifice_core.consts
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image
from artifice_core.manage_runs import save_run, save_changes, load_run

def setup_panel(translator):
    sg.theme("PANEL")

    config = artifice_core.consts.retrieve_config()


    button_size=(120,36)

    sample_types_list = ['stool', 'environmental']
    orientations_list = ['horizontal', 'vertical']
    # if sys.platform.startswith("darwin"):
    #     option_menu_text_color = '#000000'
    # else:
    #     option_menu_text_color = sg.theme_text_color()

    tooltips = {
        '-USER NAME-':translator('Username to appear in report. Default: no user name'),
        '-INSTITUTE NAME-':translator('Institute name to appear in report. Default: no institute name'),
        '-ORIENTATION-':translator('Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `horizontal`. Options: `horizontal` or `vertical`.'),
        '-SAMPLE TYPE-':translator(f'Specify sample type. Options: `stool`, `environmental`. Default: {artifice_core.consts.VALUE_SAMPLE_TYPE}'),
        '-REFERENCE SEQUENCES-':translator('Custom reference sequences file.'),
        '-POSITIVE CONTROL-':translator(f'Sample name of positive control. Default: `positive`'),
        '-NEGATIVE CONTROL-':translator('Sample name of negative control. Default: `negative`'),
        '-ANALYSIS MODE-':translator('Specify analysis mode to run. Options: `vp1`. Default: `vp1`'),
        '-MEDAKA MODEL-':translator('Medaka model to run analysis using. Default: r941_min_hac_variant_g507'),
        '-MIN MAP QUALITY-':translator('Minimum mapping quality. Default: 50'),
        '-MIN READ LENGTH-':translator('Minimum read length. Default: 1000'),
        '-MAX READ LENGTH-':translator('Maximum read length. Default: 1300'),
        '-MIN READ DEPTH-':translator('Minimum read depth required for consensus generation. Default: 50'),
        '-MIN READ PCENT-':translator('Minimum percentage of sample required for consensus generation. Default: 10'),
        '-PRIMER LENGTH-':translator('Length of primer sequences to trim off start and end of reads. Default: 30'),
        '-PUBLISH DIR-':translator('Output publish directory. Default: `analysis-2022-XX-YY`'),
        '-OUTPUT PREFIX-':translator('Prefix of output directory & report name: Default: `analysis`'),
        '-ALL META-':translator('Parse all fields from input barcode.csv file and include in the output fasta headers. Be aware spaces in metadata will disrupt the record id, so avoid these.'),
        '-DATE STAMP-':translator('Append datestamp to directory name when using <-o/--outdir>. Default: <-o/--outdir> without a datestamp'),
        '-OVERWRITE-':translator('Overwrite output directory. Default: append an incrementing number if <-o/--outdir> already exists'),
        '-VERBOSE-':translator('Print lots of stuff to screen')
    }

    basic_tab = [[
        sg.Column([ 
            [
            sg.Sizer(16,32),sg.Text(translator('User Name:'),tooltip=tooltips['-USER NAME-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Institute:'),tooltip=tooltips['-INSTITUTE NAME-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Orientation:'),tooltip=tooltips['-ORIENTATION-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Sample Type:'),tooltip=tooltips['-SAMPLE TYPE-'],),
            ],
            [sg.Sizer(16,32),]
        ],element_justification='right',pad=(0,16)),
        sg.Column([ 
            [
            sg.Sizer(16,32),sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-USER NAME-'], key='-USER NAME-',),
            ],
            [
            sg.Sizer(16,32),sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-INSTITUTE NAME-'], key='-INSTITUTE NAME-',),
            ],
            [
            sg.Sizer(16,32),sg.OptionMenu(orientations_list, default_value=orientations_list[0],tooltip=tooltips['-ORIENTATION-'],key='-ORIENTATION-'),
            ],
            [
            sg.Sizer(16,32),sg.OptionMenu(sample_types_list, default_value=sample_types_list[0],tooltip=tooltips['-SAMPLE TYPE-'],key='-SAMPLE TYPE-'),
            ],
            [sg.Sizer(16,32),sg.Checkbox(translator('Overwrite Output'), default=False, tooltip=tooltips['-OVERWRITE-'], key='-OVERWRITE-')],  
        ],pad=(0,16))

    ]]

    input_options_tab = [
        
        #Commented out for now
        #[
        #sg.Text(translate_text('Reference Sequences:',language,translate_scheme))),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-REFERENCE SEQUENCES-'], key='-REFERENCE SEQUENCES-',),
        #AltFolderBrowse(button_text=translate_text('Browse',language,translate_scheme),tooltip=tooltips['-REFERENCE SEQUENCES-'],font=font,size=button_size),
        #],
        
        [
        sg.Text(translator('Positive Control:'),tooltip=tooltips['-POSITIVE CONTROL-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=artifice_core.consts.VALUE_POSITIVE,tooltip=tooltips['-POSITIVE CONTROL-'], key='-POSITIVE CONTROL-',),
        ],
        [
        sg.Text(translator('Negative Control:'),tooltip=tooltips['-NEGATIVE CONTROL-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-NEGATIVE CONTROL-'], key='-NEGATIVE CONTROL-',),
        ],
    ]
    
    analysis_options_tab = [
        #Commented out for now
        #[
        #sg.Text(translator('Analysis Mode:'),tooltip=tooltips['-ANALYSIS MODE-']),
        #sg.Push(),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-ANALYSIS MODE-'], key='-ANALYSIS MODE-',),
        #],
        #[
        #sg.Text(translator('Medaka Model:'),tooltip=tooltips['-MEDAKA MODEL-']),
        #sg.Push(),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MEDAKA MODEL-'], key='-MEDAKA MODEL-',),
        #],
        [
        sg.Text(translator('Minimum Mapping Quality:'),tooltip=tooltips['-MIN MAP QUALITY-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN MAP QUALITY-'], key='-MIN MAP QUALITY-',),
        ],
        [
        sg.Text(translator('Minimum Read Length:'),tooltip=tooltips['-MAX READ LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MAX READ LENGTH-'], key='-MIN READ LENGTH-',),
        ],
        [
        sg.Text(translator('Maximum Read Length:'),tooltip=tooltips['-MAX READ LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MAX READ LENGTH-'], key='-MAX READ LENGTH-',),
        ],
        [
        sg.Text(translator('Minimum Read Depth:'),tooltip=tooltips['-MIN READ DEPTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN READ DEPTH-'], key='-MIN READ DEPTH-',),
        ],
        [
        sg.Text(translator('Minimum Read Percentage:'),tooltip=tooltips['-MIN READ PCENT-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN READ PCENT-'], key='-MIN READ PCENT-',),
        ],
        [
        sg.Text(translator('Primer Length:'),tooltip=tooltips['-PRIMER LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-PRIMER LENGTH-'], key='-PRIMER LENGTH-',),
        ],
    ]
    

    output_options_tab = [
        [
        sg.Text(translator('Publish Directory:'),tooltip=tooltips['-PUBLISH DIR-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-PUBLISH DIR-'], key='-PUBLISH DIR-',),
        ],
        [
        sg.Text(translator('Output Prefix:'),tooltip=tooltips['-OUTPUT PREFIX-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-OUTPUT PREFIX-'], key='-OUTPUT PREFIX-',),
        ],
        [sg.Checkbox(translator('All Metadata to Header'), default=False, tooltip=tooltips['-ALL META-'], key='-ALL META-')],
        [sg.Checkbox(translator('Date Stamp'), default=False, tooltip=tooltips['-DATE STAMP-'], key='-DATE STAMP-')], 
    ]

    misc_options_tab = [
        [sg.Checkbox('verbose', default=False, tooltip=tooltips['-VERBOSE-'], key='-VERBOSE-')],
    ]


    """
        [
        sg.Text(translate_text('Run Name',language,translate_scheme),size=(14,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=translate_text('Run name to appear in report. Default: Nanopore sequencing',language,translate_scheme), key='-RUN NAME-',),
        ],
        """
    """
     --orientation ORIENTATION
                        Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `horizontal`. Options: `horizontal` or `vertical`.
  -temp TEMPDIR, --tempdir TEMPDIR
                        Specify where you want the temp stuff to go. Default: `$TMPDIR`
  --no-temp             Output all intermediate files. For development/ debugging purposes

                        """
    
    advanced_tab = [
        [sg.TabGroup([
        [
        sg.Tab(translator('Input Options'),input_options_tab,key='-INPUT OPTIONS TAB-'),
        sg.Tab(translator('Analysis Options'),analysis_options_tab,key='-ANALYSIS OPTIONS TAB-'),
        sg.Tab(translator('Output Options'),output_options_tab,key='-OUTPUT OPTIONS TAB-'),
        sg.Tab(translator('Misc Options'),misc_options_tab,key='-MISC OPTIONS TAB-')
        ]
            ],)
        ]
    ]
    

    layout = [
    [sg.TabGroup([
        [
        sg.Tab(translator('Basic'),basic_tab,key='-BASIC OPTIONS TAB-'),
        sg.Tab(translator('Advanced'),advanced_tab,key='-ADVANCED OPTIONS TAB-'),
    ]
    ])],
    
    #[AltButton(button_text=translator('Confirm'),size=button_size,font=font,key='-CONFIRM-'),],
    ]

    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,16))

    return panel

def create_piranha_options_window(theme = 'Artifice', version = 'ARTIFICE', window = None):
    update_log('creating add protocol window')

    config = artifice_core.consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
    translator = lambda text : translate_text(text, language, translate_scheme)

    panel = setup_panel(translator)

    content = artifice_core.window_functions.setup_content(panel, translator, small=True, button_text='Continue', button_key='-CONFIRM-')

    layout = artifice_core.window_functions.setup_header_footer(content, small=True)

    piranha_scaled = scale_image('piranha.png',1,(64,64))
    new_window = sg.Window(version, layout, resizable=False, enable_close_attempted_event=True, finalize=True,icon=piranha_scaled, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_piranha_options_window(window, run_info, version = 'ARTIFICE'):
    config = artifice_core.consts.retrieve_config()
    selected_run_title = run_info['title']

    element_dict = {'-POSITIVE CONTROL-':'-pc',
                    '-NEGATIVE CONTROL-':'-nc',
                    '-SAMPLE TYPE-':'-s', 
                    #'-ANALYSIS MODE-':'m',
                    #'-MEDAKA MODEL-':'--medaka-model',
                    '-MIN MAP QUALITY-':'-q',
                    '-MIN READ LENGTH-':'-n',
                    '-MAX READ LENGTH-':'-x',
                    '-MIN READ DEPTH-':'-d',
                    '-MIN READ PCENT-':'-p',
                    '-PRIMER LENGTH-':'--primer-length',
                    '-PUBLISH DIR-':'-pub',
                    '-OUTPUT PREFIX-':'-pre',
                    '-ALL META-':'--all-metadata-to-header',
                    '-DATE STAMP-':'--datestamp',
                    '-OVERWRITE-':'--overwrite',
                    '-USER NAME-':'--username',
                    '-INSTITUTE NAME-':'--institute',
                    '-ORIENTATION-':'--orientation',
                    '-VERBOSE-':'--verbose'}
    run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], update_archive_button=False, clear_previous=False)
    
    window['-SAMPLE TYPE-'].update(size=(100,100))
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [piranha options window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return run_info
       
        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()
