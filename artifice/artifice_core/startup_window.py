import PySimpleGUI as sg

import artifice_core.start_rampart

def setup_layout(theme='Dark', font = None):
    sg.theme(theme)

    docker_installed = artifice_core.start_rampart.check_for_docker()
    if docker_installed:
        docker_status = 'Docker installed'
    else:
        docker_status = 'Docker not installed'

    got_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, artifice_core.consts.RAMPART_IMAGE, font=font)

    if not got_image:
        window.close()
        return None

    layout = [
    [
    sg.Text(docker_status,size=(14,1)),
    ],
    [
    sg.Text('MinKnow run:',size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-MINKNOW-',),
    sg.FolderBrowse(),
    ],
    [
    sg.Text('Output Folder:',size=(14,1)),
    sg.In(size=(25,1), enable_events=True,expand_y=False, key='-OUTDIR-',),
    sg.FolderBrowse(),
    ],
    [sg.Button(button_text='Confirm',key='-CONFIRM-'),],
    ]


    return layout
