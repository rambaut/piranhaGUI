import PySimpleGUI as sg
import os.path

#Window for user to select samples csv and possibling MinKnow

def setup_selection_layout(theme = 'Dark'):
    sg.theme(theme)

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

def create_select_window(theme = 'Artifice', font = ('FreeSans', 18), window = None):
    layout = setup_selection_layout(theme=theme)
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
                samples = values['-SAMPLES-'].strip()
                MinKnow = values['-MINKNOW-'].strip()

                if os.path.isfile(samples) == False:
                    raise Exception('Invalid samples file')

                if os.path.isdir(MinKnow) == False and MinKnow != '':
                    raise Exception('Invalid MinKnows')

                window.close()
                return samples, MinKnow, values['-HEADERS CHECKBOX-']
            except Exception as err:
                sg.popup_error(err)

    window.close()
    return None


if __name__ == '__main__':

    window = create_select_window()
    run_select_window(window)

    window.close()
