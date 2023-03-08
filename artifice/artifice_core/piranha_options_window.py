import PySimpleGUI as sg
import sys

import artifice_core.consts
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image
from artifice_core.manage_runs import save_run, save_changes, load_run

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
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    button_size=(120,36)

    sample_types_list = ['stool', 'environmental']
    orientations_list = ['horizontal', 'vertical']
    if sys.platform.startswith("darwin"):
        option_menu_text_color = '#000000'
    else:
        option_menu_text_color = sg.theme_text_color()

    tooltips = {
        '-USER NAME-':translate_text('Username to appear in report. Default: no user name',language,translate_scheme),
        '-INSTITUTE NAME-':translate_text('Institute name to appear in report. Default: no institute name',language,translate_scheme),
        '-ORIENTATION-':translate_text('Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `horizontal`. Options: `horizontal` or `vertical`.',language,translate_scheme),
        '-SAMPLE TYPE-':translate_text('Specify sample type. Options: `stool`, `environmental`. Default: `stool`',language,translate_scheme),
        '-REFERENCE SEQUENCES-':translate_text('Custom reference sequences file.',language,translate_scheme),
        '-POSITIVE CONTROL-':translate_text('Sample name of positive control. Default: `positive`',language,translate_scheme),
        '-NEGATIVE CONTROL-':translate_text('Sample name of negative control. Default: `negative`',language,translate_scheme),
        '-ANALYSIS MODE-':translate_text('Specify analysis mode to run. Options: `vp1`. Default: `vp1`',language,translate_scheme),
        '-MEDAKA MODEL-':translate_text('Medaka model to run analysis using. Default: r941_min_hac_variant_g507',language,translate_scheme),
        '-MIN MAP QUALITY-':translate_text('Minimum mapping quality. Default: 50',language,translate_scheme),
        '-MIN READ LENGTH-':translate_text('Minimum read length. Default: 1000',language,translate_scheme),
        '-MAX READ LENGTH-':translate_text('Maximum read length. Default: 1300',language,translate_scheme),
        '-MIN READ DEPTH-':translate_text('Minimum read depth required for consensus generation. Default: 50',language,translate_scheme),
        '-MIN READ PCENT-':translate_text('Minimum percentage of sample required for consensus generation. Default: 10',language,translate_scheme),
        '-PRIMER LENGTH-':translate_text('Length of primer sequences to trim off start and end of reads. Default: 30',language,translate_scheme),
        '-PUBLISH DIR-':translate_text('Output publish directory. Default: `analysis-2022-XX-YY`',language,translate_scheme),
        '-OUTPUT PREFIX-':translate_text('Prefix of output directory & report name: Default: `analysis`',language,translate_scheme),
        '-ALL META-':translate_text('Parse all fields from input barcode.csv file and include in the output fasta headers. Be aware spaces in metadata will disrupt the record id, so avoid these.',language,translate_scheme),
        '-DATE STAMP-':translate_text('Append datestamp to directory name when using <-o/--outdir>. Default: <-o/--outdir> without a datestamp',language,translate_scheme),
        '-OVERWRITE-':translate_text('Overwrite output directory. Default: append an incrementing number if <-o/--outdir> already exists',language,translate_scheme),
        '-VERBOSE-':translate_text('Print lots of stuff to screen',language,translate_scheme)
    }

    basic_tab = [   
        [
        sg.Text(translate_text('User Name:',language,translate_scheme),tooltip=tooltips['-USER NAME-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-USER NAME-'], key='-USER NAME-',),
        ],
        [
        sg.Text(translate_text('Institute:',language,translate_scheme),tooltip=tooltips['-INSTITUTE NAME-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-INSTITUTE NAME-'], key='-INSTITUTE NAME-',),
        ],
        [
        sg.Text(translate_text('Orientation:',language,translate_scheme),tooltip=tooltips['-ORIENTATION-']),
        sg.Push(),
        sg.OptionMenu(orientations_list, default_value=orientations_list[0],text_color=option_menu_text_color,tooltip=tooltips['-ORIENTATION-'],key='-ORIENTATION-'),
        ],
        [
        sg.Text(translate_text('Sample Type:',language,translate_scheme),tooltip=tooltips['-SAMPLE TYPE-'],),
        sg.Push(),
        sg.OptionMenu(sample_types_list, default_value=sample_types_list[0],text_color=option_menu_text_color,tooltip=tooltips['-SAMPLE TYPE-'],key='-SAMPLE TYPE-'),
        ],
        [sg.Checkbox(translate_text('Overwrite Output',language,translate_scheme), default=False, tooltip=tooltips['-OVERWRITE-'], key='-OVERWRITE-')],  
        ]

    input_options_tab = [
        
        #Commented out for now
        #[
        #sg.Text(translate_text('Reference Sequences:',language,translate_scheme))),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-REFERENCE SEQUENCES-'], key='-REFERENCE SEQUENCES-',),
        #AltFolderBrowse(button_text=translate_text('Browse',language,translate_scheme),tooltip=tooltips['-REFERENCE SEQUENCES-'],font=font,size=button_size),
        #],
        
        [
        sg.Text(translate_text('Positive Control:',language,translate_scheme),tooltip=tooltips['-POSITIVE CONTROL-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-POSITIVE CONTROL-'], key='-POSITIVE CONTROL-',),
        ],
        [
        sg.Text(translate_text('Negative Control:',language,translate_scheme),tooltip=tooltips['-NEGATIVE CONTROL-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-NEGATIVE CONTROL-'], key='-NEGATIVE CONTROL-',),
        ],
    ]
    
    analysis_options_tab = [
        #Commented out for now
        #[
        #sg.Text(translate_text('Analysis Mode:',language,translate_scheme),tooltip=tooltips['-ANALYSIS MODE-']),
        #sg.Push(),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-ANALYSIS MODE-'], key='-ANALYSIS MODE-',),
        #],
        #[
        #sg.Text(translate_text('Medaka Model:',language,translate_scheme),tooltip=tooltips['-MEDAKA MODEL-']),
        #sg.Push(),
        #sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MEDAKA MODEL-'], key='-MEDAKA MODEL-',),
        #],
        [
        sg.Text(translate_text('Minimum Mapping Quality:',language,translate_scheme),tooltip=tooltips['-MIN MAP QUALITY-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN MAP QUALITY-'], key='-MIN MAP QUALITY-',),
        ],
        [
        sg.Text(translate_text('Minimum Read Length:',language,translate_scheme),tooltip=tooltips['-MAX READ LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MAX READ LENGTH-'], key='-MIN READ LENGTH-',),
        ],
        [
        sg.Text(translate_text('Maximum Read Length:',language,translate_scheme),tooltip=tooltips['-MAX READ LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MAX READ LENGTH-'], key='-MAX READ LENGTH-',),
        ],
        [
        sg.Text(translate_text('Minimum Read Depth:',language,translate_scheme),tooltip=tooltips['-MIN READ DEPTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN READ DEPTH-'], key='-MIN READ DEPTH-',),
        ],
        [
        sg.Text(translate_text('Minimum Read Percentage:',language,translate_scheme),tooltip=tooltips['-MIN READ PCENT-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-MIN READ PCENT-'], key='-MIN READ PCENT-',),
        ],
        [
        sg.Text(translate_text('Primer Length:',language,translate_scheme),tooltip=tooltips['-PRIMER LENGTH-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-PRIMER LENGTH-'], key='-PRIMER LENGTH-',),
        ],
    ]
    

    output_options_tab = [
        [
        sg.Text(translate_text('Publish Directory:',language,translate_scheme),tooltip=tooltips['-PUBLISH DIR-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-PUBLISH DIR-'], key='-PUBLISH DIR-',),
        ],
        [
        sg.Text(translate_text('Output Prefix:',language,translate_scheme),tooltip=tooltips['-OUTPUT PREFIX-']),
        sg.Push(),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=tooltips['-OUTPUT PREFIX-'], key='-OUTPUT PREFIX-',),
        ],
        [sg.Checkbox(translate_text('All Metadata to Header',language,translate_scheme), default=False, tooltip=tooltips['-ALL META-'], key='-ALL META-')],
        [sg.Checkbox(translate_text('Date Stamp',language,translate_scheme), default=False, tooltip=tooltips['-DATE STAMP-'], key='-DATE STAMP-')], 
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
        sg.Tab(translate_text('Input Options',language,translate_scheme),input_options_tab,key='-INPUT OPTIONS TAB-'),
        sg.Tab(translate_text('Analysis Options',language,translate_scheme),analysis_options_tab,key='-ANALYSIS OPTIONS TAB-'),
        sg.Tab(translate_text('Output Options',language,translate_scheme),output_options_tab,key='-OUTPUT OPTIONS TAB-'),
        sg.Tab(translate_text('Misc Options',language,translate_scheme),misc_options_tab,key='-MISC OPTIONS TAB-')
        ]
            ],)
        ]
    ]
    

    layout = [
    [sg.TabGroup([
        [
        sg.Tab(translate_text('Basic',language,translate_scheme),basic_tab,key='-BASIC OPTIONS TAB-'),
        sg.Tab(translate_text('Advanced',language,translate_scheme),advanced_tab,key='-ADVANCED OPTIONS TAB-'),
    ]
    ])],
    
    [AltButton(button_text=translate_text('Confirm',language,translate_scheme),size=button_size,font=font,key='-CONFIRM-'),],
    ]

    return layout

def create_piranha_options_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating add protocol window')
    make_theme()
    layout = setup_layout(theme=theme, font=font)
    piranha_scaled = scale_image('piranha.png',scale,(64,64))
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,icon=piranha_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_piranha_options_window(window, run_info, font = None, version = 'ARTIFICE'):
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
                error_popup(err, font)

    window.close()
