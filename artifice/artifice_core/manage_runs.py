import os.path
import json
from os import mkdir, listdir
from shutil import rmtree, copytree

from artifice_core.update_log import log_event, update_log
import artifice_core.consts

#creates a directory containing run info json
def save_run(run_info, title = None, overwrite = False, iter = 0, runs_dir = artifice_core.consts.RUNS_DIR):
    samples = run_info['samples']
    if title == None or title == '':
        title = samples.split('/')[-1].split('.')[0]

    original_title = title

    if iter > 0:
        title = title+'('+str(iter)+')'

    update_log(f'saving run: "{title}"...')

    filepath = runs_dir+'/'+title+'/run_info.json'


    if overwrite == False:
        if os.path.isfile(filepath):
            update_log(f'run: "{title}" already exists, adding iterator')
            return save_run(run_info,title=original_title,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    if not os.path.isdir(runs_dir+'/'+title):
        mkdir(runs_dir+'/'+title)

    for key, value in run_info.items():
        if type(run_info[key]) == str:
            run_info[key] = value.strip()

    run_info['title'] = title

    with open(filepath, 'w') as file:
        json.dump(run_info, file)

    return title

def save_changes(values, run_info, window, rename = False, overwrite = True, hide_archived = True):
    title = run_info['title']
    run_info = get_run_info(values, run_info)
    update_log(title)
    if rename:
        title = run_info['title']
    else:
        run_info['title'] = title
    update_log(title)
    title = save_run(run_info, title=title, overwrite=overwrite)
    run_info = update_run_list(window, run_info, run_to_select=title, hide_archived=hide_archived)

    return run_info

def delete_run(title, window, clear_selected = True, runs_dir = artifice_core.consts.RUNS_DIR):
    update_log(f'deleting run: "{title}"')
    filepath = runs_dir+'/'+title

    if os.path.isdir(filepath):
        rmtree(filepath)

    if clear_selected:
        clear_selected_run(window)

def get_run_info(values, run_info):
    run_info['title'] = values['-INFOTAB-RUN NAME-'].strip()
    run_info['description'] = values['-INFOTAB-RUN DESCR-'].strip()
    run_info['samples'] = values['-INFOTAB-SAMPLES-'].strip()
    run_info['basecalledPath'] = values['-INFOTAB-MINKNOW-'].strip()

    return run_info

#retrieve the paths of directories in the run folder
def get_runs(runs_dir = artifice_core.consts.RUNS_DIR, archived_json = artifice_core.consts.ARCHIVED_RUNS, hide_archived = True):
    paths = listdir(runs_dir)
    runs_set = set()
    for path in paths:
        if os.path.isdir(runs_dir+'/'+path):
            runs_set.add(path)

    if hide_archived:
        archived_filepath = runs_dir+'/'+archived_json+'.json'

        with open(archived_filepath,'r') as file:
            archived_runs_dict = json.loads(file.read())

        archived_runs = archived_runs_dict['archived_runs']
        for run in archived_runs:
            try:
                runs_set.remove(run)
            except:
                continue

    runs = list(runs_set)

    return runs

def load_run(window, title, runs_dir = artifice_core.consts.RUNS_DIR):
    update_log(f'loading run: "{title}"...')
    filepath = runs_dir+'/'+title+'/run_info.json'

    with open(filepath,'r') as file:
        run_info = json.loads(file.read())
        try:
            window['-INFOTAB-DATE-'].update(run_info['date'])
        except:
            window['-INFOTAB-DATE-'].update('')

        try:
            window['-INFOTAB-RUN NAME-'].update(run_info['title'])
        except:
            window['-INFOTAB-RUN NAME-'].update('')

        try:
            window['-INFOTAB-RUN DESCR-'].update(run_info['description'])
        except:
            window['-INFOTAB-RUN DESCR-'].update('')

        try:
            window['-INFOTAB-SAMPLES-'].update(run_info['samples'])
        except:
            window['-INFOTAB-SAMPLES-'].update('')

        try:
            window['-INFOTAB-MINKNOW-'].update(run_info['basecalledPath'])
        except:
            window['-INFOTAB-MINKNOW-'].update('')

    if 'archived' not in run_info:
        run_info['archived'] = False

    if run_info['archived'] == True:
        window['-INFOTAB-ARCHIVE/UNARCHIVE-'].update(text='Unarchive')
    else:
        window['-INFOTAB-ARCHIVE/UNARCHIVE-'].update(text='Archive')

    return run_info

def clear_selected_run(window):
    update_log('clearing run info tab')
    window['-INFOTAB-DATE-'].update('')
    window['-INFOTAB-RUN NAME-'].update('')
    window['-INFOTAB-RUN DESCR-'].update('')
    window['-INFOTAB-SAMPLES-'].update('')
    window['-INFOTAB-MINKNOW-'].update('')

    return {}

def update_run_list(window, run_info, run_to_select = '', hide_archived = True):
    update_log(f'updating run list')
    runs = get_runs(hide_archived=hide_archived)
    window['-RUN LIST-'].update(values=runs)

    if run_to_select == '':
        if 'title' in run_info:
            run_to_select = run_info['title']
        else:
            return run_info


    run_info = {}
    #update_log(str(runs))
    #update_log(str(run_to_select))
    for i in range(len(runs)):
        if runs[i] == run_to_select:
            update_log(f'selecting run: {run_to_select}')
            window['-RUN LIST-'].update(set_to_index=i)
            run_info = load_run(window, run_to_select)

    if run_info == {}:
        run_info = clear_selected_run(window)

    return run_info

def edit_archive(title, window, runs_dir = artifice_core.consts.RUNS_DIR, archived_runs = artifice_core.consts.ARCHIVED_RUNS, clear_selected = True, archive = True):
    archived_filepath = runs_dir+'/'+archived_runs+'.json'

    with open(archived_filepath,'r') as file:
        archived_runs_dict = json.loads(file.read())

    if archive:
        update_log(f'archiving run: {title}')
        archived_runs_dict['archived_runs'].append(title)
    else:
        try:
            update_log(f'unarchiving run: {title}')
            archived_runs_dict['archived_runs'].remove(title)
        except:
            update_log('unarchive failed, run probably not archived')
            pass

    with open(archived_filepath,'w') as file:
        archived_json = json.dump(archived_runs_dict, file)

    if clear_selected:
        clear_selected_run(window)

def rename_run(values, run_info, window, hide_archived = True, runs_dir = artifice_core.consts.RUNS_DIR):
    previous_run_title = values['-RUN LIST-'][0]
    run_info = get_run_info(values, run_info)
    new_title = run_info['title']
    if new_title != previous_run_title:
        update_log(f'renaming run: "{previous_run_title}" to "{new_title}"')

        #this is just to get a new title in the event the new name already matches a run
        run_info = save_changes(values, run_info, window, rename=True, overwrite=False, hide_archived=hide_archived)
        new_title = run_info['title']
        delete_run(new_title, window, clear_selected=False)
        update_log('moving files to new directory')
        try:
            copytree(f'{runs_dir}/{previous_run_title}', f'{runs_dir}/{new_title}')
        except Exception as err:
            print('failed to copy some file(s)')
            update_log(traceback.format_exc())

        #update_log(f'run_info: {run_info}')
        run_info = save_changes(values, run_info, window, rename=False, overwrite=True, hide_archived=hide_archived)
        #update_log(f'run_info: {run_info}')
        edit_archive(new_title, window, archive=run_info['archived'])
        edit_archive(previous_run_title, window, archive=False)
        delete_run(previous_run_title, window, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)
