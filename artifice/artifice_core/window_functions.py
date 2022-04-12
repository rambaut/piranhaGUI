import PySimpleGUI as sg
import queue
import threading

import artifice_core.start_rampart
from artifice_core.update_log import log_event, update_log

# prints the queued log output until it's empty, prints a message if container stopped
def print_container_log(log_queue, window, output_key, logfile):
    queue_empty = False
    while not queue_empty:
        try:
            output = log_queue.get(block=False)
            log_queue.task_done()
            window[output_key].print(output, end='')
            update_log(output, filename=logfile, add_newline=False)
            if output == '###CONTAINER STOPPED###\n':
                return True
        except queue.Empty:
            queue_empty = True
            pass

    return False

# asks the user whether they would like to stop the running container(s) when they close the window
def check_stop_on_close(names: list, window, client, container, font = None):
    to_stop = []
    for name in names:
        chk_stop = sg.popup_yes_no(f'Do you wish to stop {name} while closing?', font=font)
        if chk_stop == 'Yes':
            to_stop.append(name)
        else:
            update_log(f'User chose to keep {name} running')

    window.close()

    for name in to_stop:
        container_name = name.lower()
        update_log(f'stopping {name}...')
        artifice_core.start_rampart.stop_docker(client=client, container=None, container_name=container_name)
        update_log(f'{name} stopped')

# queues the log output from already running container
def get_pre_log(client, log_queue, container_name):
    container = client.containers.get(container_name)
    log = container.logs(stream=True)
    log_thread = threading.Thread(target=artifice_core.start_rampart.queue_log, args=(log, log_queue), daemon=True)
    log_thread.start()

    return container

# checks if container running
def setup_check_container(tool_name):
    update_log(f'checking if {tool_name} is running...')
    running = False

    if tool_name == 'RAMPART':
        running = artifice_core.start_rampart.check_rampart_running()
    else:
        container_name = tool_name.lower()
        running = artifice_core.start_rampart.check_container(container_name)

    if running:
        button_text = f'Stop {tool_name}'
        status = f'{tool_name} is running'
    else:
        button_text = f'Start {tool_name}'
        status = f'{tool_name} is not running'

    return running, button_text, status
