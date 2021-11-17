#launches hello world GUI window
import PySimpleGUI as sg

layout = [[sg.Text('Hello, World. This is a test GUI')], [sg.Button('OK')]]

window = sg.Window(title='Hello, World', layout = layout, margins = (200,100))

while True:
    event, values = window.read()

    #end program if user closes window or presses button
    if event == 'OK' or event == sg.WIN_CLOSED:
        break
