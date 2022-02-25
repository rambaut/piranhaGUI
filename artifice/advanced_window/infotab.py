import PySimpleGUI as sg
import traceback

import artifice_core.parse_columns_window
from artifice_core.manage_runs import save_run, delete_run, rename_run, update_run_list, edit_archive, save_changes, clear_selected_run, load_run
from artifice_core.update_log import log_event, update_log

def archive_button(run_info, window, values, hide_archived, element_dict=None):
    if 'archived' not in run_info:
        run_info['archived'] = False

    if run_info['archived'] == True:
        run_info['archived'] = False
        run_info = save_changes(values, run_info, window, hide_archived=hide_archived, element_dict=element_dict)
        edit_archive(run_info['title'], window, archive=False, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived, element_dict=element_dict)

    else:
        run_info['archived'] = True
        run_info = save_changes(values, run_info, window, hide_archived=hide_archived, element_dict=element_dict)
        edit_archive(run_info['title'], window, archive=True, clear_selected=True)
        if hide_archived:
            run_info = {}
            run_info = update_run_list(window, run_info, hide_archived=hide_archived, element_dict=element_dict)
        else:
            run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived, element_dict=element_dict)

    return run_info

def infotab_event(event, run_info, selected_run_title, hide_archived, element_dict, font, values, window):
    event = event[8:]

    if event == '-VIEW SAMPLES-':
        try:
            artifice_core.parse_columns_window.view_samples(run_info, values, '-INFOTAB-SAMPLES-', font)
            selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)

    elif event == '-DELETE RUN-':
        if 'title' in run_info:
            try:
                user_confirm = sg.popup_ok_cancel('Are you sure you want to delete this run?',font=font)
                if user_confirm != 'OK':
                    update_log('deletion cancelled')
                    return run_info, selected_run_title
                selected_run_title = values['-RUN LIST-'][0]
                delete_run(selected_run_title, window)
                run_info = {}
                run_info = update_run_list(window, run_info, hide_archived=hide_archived, element_dict=element_dict)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    elif event == '-ARCHIVE/UNARCHIVE-':
        if 'title' in run_info:
            try:
                run_info = archive_button(run_info, window, values, hide_archived, element_dict=element_dict)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    elif event == '-RUN NAME-FocusOut':
        try:
            if 'title' in run_info:
                rename_run(values, run_info, window, hide_archived=hide_archived, element_dict=element_dict)
            else:
                clear_selected_run(window)
        except Exception as err:
            sg.popup_error(err)
            try:
                update_log(traceback.format_exc())
                run_info = load_run(window, run_info['title'])
            except Exception as err:
                sg.popup_error(err)

    elif event in {'-RUN DESCR-FocusOut','-SAMPLES-FocusOut','-MINKNOW-FocusOut'}:
        try:
            if 'title' in run_info:
                run_info = save_changes(values, run_info, window, hide_archived=hide_archived, element_dict=element_dict)
            else:
                clear_selected_run(window)
        except Exception as err:
            update_log(traceback.format_exc())
            sg.popup_error(err)
            try:
                run_info = load_run(window, run_info['title'])
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    return run_info, selected_run_title, window
