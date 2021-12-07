import PySimpleGUI as sg
import os.path

#Window for user to select samples csv and possibling MinKnow

def setup_selection_layout():

    layout = [
        [
        sg.Text('Samples',size=(25,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        ],
        [
        sg.Text('MinKnow run (optional)',size=(25,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
        sg.FileBrowse(),
        ],
        [
        sg.Button(button_text='Next',key='-NEXT-'),
        ],
    ]

    return layout

def create_select_window(theme = 'Dark', font = ('FreeSans', 18), window = None):
    layout = setup_selection_layout()
    new_window = sg.Window('Artifice', layout, font=font, resizable=True)

    if window != None:
        window.close()

    return new_window

def run_select_window(window):
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == '-NEXT-':
            try:
                if os.path.isfile(values['-SAMPLES-']) == False:
                    raise Exception('Invalid samples file')
                window.close()
                return values['-SAMPLES-'], values['-MINKNOW-']
            except Exception as err:
                sg.popup_error(err)

    window.close()
    return None


if __name__ == '__main__':

    window = create_select_window()
    run_select_window(window)

    window.close()
