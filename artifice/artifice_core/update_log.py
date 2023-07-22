import artifice_core.consts as consts

#update the log with a new line
def update_log(line, filename = consts.LOGFILE, overwrite = False, add_newline = True):
    #make sure line can be converted to string
    try:
        line = str(line)
    except:
        return

    if overwrite:
        mode = 'w'
    else:
        mode = 'a'

    filepath = str(consts.get_datadir() / filename)

    #limits the length of the line to 200 characters :- DISUSED
    #if len(line) > 200:
    #    line = f'{line[0:148]}...{line[-50:]}'

    with open(filepath, mode) as f:
        if add_newline:
            f.write(line+'\n')
        else:
            f.write(line)

# lazy function to log a PySimpleGUI event 
def log_event(input, filename = consts.LOGFILE):
    update_log(f'\nEVENT: {input}', filename)
