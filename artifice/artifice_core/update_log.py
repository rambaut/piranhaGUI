import artifice_core.consts

#update the log with a new line
def update_log(line, filename = artifice_core.consts.LOGFILE, overwrite = False, add_newline = True):
    if overwrite:
        mode = 'w'
    else:
        mode = 'a'

    filepath = str(artifice_core.consts.get_datadir() / filename)

    #limits the length of the line to 200 characters :- DISUSED
    #if len(line) > 200:
    #    line = f'{line[0:148]}...{line[-50:]}'

    with open(filepath, mode) as f:
        if add_newline:
            f.write(line+'\n')
        else:
            f.write(line)

def log_event(input, filename = artifice_core.consts.LOGFILE):
    update_log(f'\nEVENT: {input}', filename)
