import os.path
import json
import traceback
import csv
import os.path
import traceback
import pandas as pd
from os import mkdir, listdir
from shutil import rmtree, copytree

from artifice_core.update_log import log_event, update_log
import artifice_core.consts as consts

# creates a directory containing run info json
def save_run(run_info, title = None, runs_dir = None, overwrite = False, iter = 0):
    samples = run_info['samples']
    if title == None or title == '':
        title = samples.split('/')[-1].split('.')[0]

    original_title = title

    if iter > 0:
        title = title+'('+str(iter)+')'

    update_log(f'saving run: "{title}"...')


    if not runs_dir:
        runs_dir = consts.RUNS_DIR

    filepath = runs_dir / title / 'run_info.json'

    if overwrite == False:
        if os.path.isfile(filepath):
            update_log(f'run: "{title}" already exists, adding iterator')
            return save_run(run_info,title=original_title,overwrite=overwrite,iter=iter+1)

    if os.path.isfile(samples) == False or not samples.endswith(('.csv','.xls','.xlsx')): #samples[-4:] != '.csv':
        raise Exception('No valid samples file provided')

    if not os.path.isdir(runs_dir / title):
        mkdir(runs_dir / title)

    for key, value in run_info.items():
        if type(run_info[key]) == str:
            run_info[key] = value.strip()

    run_info['title'] = title

    with open(filepath, 'w') as file:
        json.dump(run_info, file)

    return title

# old function for 'advanced' window
def save_changes(values, run_info, window, rename = False, overwrite = True, hide_archived = True, element_dict = None, update_list = True):
    title = run_info['title']
    run_info = get_run_info(values, run_info, element_dict)
    update_log(title)
    if rename:
        title = run_info['title']
    else:
        run_info['title'] = title
    update_log(title)
    title = save_run(run_info, title=title, overwrite=overwrite)

    if update_list:
        run_info = update_run_list(window, run_info, run_to_select=title, hide_archived=hide_archived, element_dict=element_dict)

    return run_info

def delete_run(title, window, runs_dir = None, clear_selected = True):
    update_log(f'deleting run: "{title}"')

    edit_archive(title, window, clear_selected=False, archive=False) #unarchiving to avoid bugs if a new run with the same name is created

    if not runs_dir:
        runs_dir = consts.RUNS_DIR

    filepath = runs_dir / title

    if os.path.isdir(filepath):
        rmtree(filepath)

    if clear_selected:
        clear_selected_run(window)

def get_run_info(values, run_info, element_dict):
    """
    run_info['title'] = values['-INFOTAB-RUN NAME-'].strip()
    run_info['description'] = values['-INFOTAB-RUN DESCR-'].strip()
    run_info['samples'] = values['-INFOTAB-SAMPLES-'].strip()
    run_info['basecalledPath'] = values['-INFOTAB-MINKNOW-'].strip()
    """
    try:
        for element in element_dict:
            if element in values:
                if type(values[element]) == str:
                    run_info[element_dict[element]] = values[element].strip()
                else:
                    run_info[element_dict[element]] = values[element]
    except:
        pass

    return run_info

# retrieve the paths of directories in the run folder
def get_runs(runs_dir = None, archived_json = None, hide_archived = True):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR
    
    if not archived_json:
        archived_json = consts.ARCHIVED_RUNS

    paths = listdir(runs_dir)
    runs_set = set()
    for path in paths:
        if os.path.isdir(runs_dir / path):
            runs_set.add(path)

    if hide_archived:
        archived_filepath = runs_dir / str(archived_json+'.json')

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
    
# loads run info into window elemnts
def load_run(window, title, element_dict, runs_dir = None, update_archive_button = True, clear_previous = True):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR
    
    update_log(f'loading run: "{title}"...')
    filepath = runs_dir / title / 'run_info.json'

    with open(filepath,'r') as file:
        run_info = json.loads(file.read())

    for element in element_dict:
        #print(f'{element}:{run_info[element_dict[element]]}')
        try:
            if element_dict[element] in run_info:
                window[element].update(run_info[element_dict[element]])
        except:
            if clear_previous:
                window[element].update('')

    if 'archived' not in run_info:
        run_info['archived'] = False

    if update_archive_button:
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

def update_run_list(window, run_info, run_to_select = '', hide_archived = True, element_dict = None):
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
            run_info = load_run(window, run_to_select, element_dict)

    if run_info == {}:
        run_info = clear_selected_run(window)

    return run_info

def edit_archive(title, window, runs_dir = None, archived_runs = None, clear_selected = True, archive = True):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR
    if not archived_json:
        archived_json = consts.ARCHIVED_RUNS

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

def rename_run(values, run_info, window, hide_archived = True, runs_dir = None, element_dict = None):
    if not runs_dir:
        runs_dir = consts.RUNS_DIR

    previous_run_title = values['-RUN LIST-'][0]
    run_info = get_run_info(values, run_info, element_dict)
    new_title = run_info['title']
    if new_title != previous_run_title:
        update_log(f'renaming run: "{previous_run_title}" to "{new_title}"')

        #this is just to get a new title in the event the new name already matches a run
        run_info = save_changes(values, run_info, window, rename=True, overwrite=False, hide_archived=hide_archived, element_dict=element_dict)
        new_title = run_info['title']
        delete_run(new_title, window, clear_selected=False)
        update_log('moving files to new directory')
        try:
            #copytree(f'{runs_dir}/{previous_run_title}', f'{runs_dir}/{new_title}')
            copytree(runs_dir / previous_run_title, runs_dir / new_title)
        except Exception as err:
            print('failed to copy some file(s)')
            update_log(traceback.format_exc())

        #update_log(f'run_info: {run_info}')
        run_info = save_changes(values, run_info, window, rename=False, overwrite=True, hide_archived=hide_archived)
        #update_log(f'run_info: {run_info}')
        edit_archive(new_title, window, archive=run_info['archived'])
        edit_archive(previous_run_title, window, archive=False)
        delete_run(previous_run_title, window, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived, element_dict=element_dict)

# return a list with the samples from given file
def samples_to_list(filepath, has_headers = True, trim = True):
    if not os.path.isfile(filepath):
        raise Exception('Samples files missing')
    
    filepath = str(filepath)

    if filepath.endswith('.csv'):
        samples_list, column_headers = csv_to_list(filepath, has_headers=has_headers, trim=trim)

    elif filepath.endswith('.xls') or filepath.endswith('.xlsx'):
        samples_frame = pd.read_excel(filepath)
        samples_list, column_headers = excel_to_list(filepath, has_headers=has_headers)

        #raise Exception('Excel files are not supported')


    return samples_list, column_headers

# return a list with the samples from given csv file
def csv_to_list(filepath, has_headers = True, trim = True):
    with open(filepath, newline = '') as csvfile:
        try:
            csvreader = csv.reader(csvfile)
            csv_list = list(csvreader)
        except Exception as err:
            raise Exception('Invalid CSV file')
        
    if trim:
        for row in csv_list:
            for i in range(len(row)):
                row[i] = row[i].strip()
                row[i] = row[i].strip('\ufeff') # remove characters added by excel
                row[i] = row[i].strip()

    samples_list, column_headers = get_headers(csv_list, has_headers)

    return samples_list, column_headers

def excel_to_list(filepath, has_headers = True):
    samples_frame = pd.read_excel(filepath)
    first_row = list(samples_frame.columns)
    data_list = samples_frame.values.tolist()
    data_list.insert(0,first_row)
    #print(data_list)

    #check if matches template
    header_row = find_header_row(data_list)
    if header_row > 0:
        print(get_options_from_excel(data_list,header_row))
   
    samples_list, column_headers = get_headers(data_list, has_headers, header_row=header_row)
    print(column_headers)
 
    return samples_list, column_headers

def find_header_row(data_list, headers = ['barcode', 'sample'], default = 0): #for finding where headers start in excel
    #if not any#list[0][0] == 'Date of run:':
    for i in range(len(data_list)):
        for j in range(len(data_list[i])):
            if any(data_list[i][j] == header for header in ['barcode', 'sample']): #list[i][0] == 'barcode':
                return i
    return default

def get_options_from_excel(data_list, header_row):
    options = {}
    for i in range(header_row):
        print(i)
        print(data_list[i][0])
        options[data_list[i][0]] = data_list[i][1]
    return options

def get_headers(data_list, has_headers, header_row = 0):
    if has_headers:
        column_headers = data_list[header_row]
        samples_list = data_list[header_row+1:]
    else:
        column_headers = []
        for i in range(1,len(data_list[0])+1):
            column_headers.append(str(i))
        samples_list = data_list
    return samples_list, column_headers

# searches column headers for given string
def find_column(column_headers, string, case_sensitive = False):
    headers = column_headers.copy()

    if not case_sensitive:
        string = string.lower()
        for i in range(len(headers)):
            headers[i] = str(headers[i]).lower()

    candidates = []
    for i in range(len(headers)):
        if string in headers[i]:
            candidates.append(i)
    
    if len(candidates) == 0:
        return None
    elif len(candidates) == 1:
        return candidates[0]
    else:
        for i in candidates:
            if headers[i] == string:
                return i
        return candidates[0]
     
    
    return None
            
def set_default_columns(column_headers, run_info, barcodes_column = None, samples_column = None):
    if barcodes_column == None:
        if 'barcodes_column' in run_info:
                barcodes_column = run_info['barcodes_column']
        else:
            barcodes_column = find_column(column_headers, 'barcode')

    if samples_column == None:
        if 'samples_column' in run_info:
            samples_column = run_info['samples_column']
        else:
            samples_column = find_column(column_headers, 'sample')
    
    # sets the columns if no match found
    if barcodes_column == None:
        if samples_column == None:
            barcodes_column = 0
            samples_column = 1
            return barcodes_column, samples_column
        elif samples_column > 0:
            barcodes_column = samples_column - 1
        else:
            barcodes_column = samples_column + 1
    
    if samples_column == None:
        if barcodes_column > 0:
            samples_column = barcodes_column - 1
        else:
            samples_column = barcodes_column + 1

    
    return barcodes_column, samples_column

def set_report_language(run_info, config): #adds language to options
    language = config['LANGUAGE']
    if language == 'Français':
        language = 'French'
    else:
        language = 'English'

    print(language)
    run_info['--language'] = language
    run_info['title'] = save_run(run_info, title=run_info['title'], overwrite=True)

    return run_info

# this function looks for (sub)directory containing barcodes from given directory, hopefully to correct user error, also returns run name based on directories
def look_for_barcodes(minknow_dir):
    minknow_base_dir = os.path.basename(minknow_dir)
    minknow_list_dir = os.listdir(minknow_dir)
    minknow_list_dir = filter(os.path.isdir, [os.path.join(minknow_dir, dir) for dir in minknow_list_dir])

    if minknow_base_dir == 'demultiplexed': #'fastq_pass':
        run_name = os.path.basename(os.path.dirname(os.path.dirname(minknow_dir)))
        return minknow_dir, run_name
    else:
        for dir in minknow_list_dir:
            new_dir, run_name = look_for_barcodes(dir)
            if new_dir != None:
                return new_dir, run_name
     
    return None, None
            #if dir == 'demultiplexed':
            #    return os.path.join(minknow_dir,dir)


            
def check_file_utf8(filepath):
    with open(filepath) as file:
        try:
            data = file.decode('utf-8')
        except:
            data = None

        if data == None:
            return False
        else:
            return True

def check_supp_datadir(dirpath):
    supp_list = os.listdir(dirpath)
    supp_file_list = filter(os.path.isfile, [os.path.join(dirpath, file) for file in supp_list])

    for file in supp_file_list:
        if file.endswith('.fasta') or file.endswith('.fa'):
            if check_file_utf8(file):
                return True
    
    return False