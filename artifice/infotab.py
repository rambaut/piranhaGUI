import PySimpleGUI as sg
import parse_columns_window
import view_barcodes_window
import traceback

from manage_runs import save_run, delete_run, rename_run, update_run_list, edit_archive, save_changes, clear_selected_run, load_run
from update_log import log_event, update_log

def archive_button(run_info, window, values, hide_archived):
    if 'archived' not in run_info:
        run_info['archived'] = False

    if run_info['archived'] == True:
        run_info['archived'] = False
        run_info = save_changes(values, run_info, window, hide_archived=hide_archived)
        edit_archive(run_info['title'], window, archive=False, clear_selected=False)
        run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)

    else:
        run_info['archived'] = True
        run_info = save_changes(values, run_info, window, hide_archived=hide_archived)
        edit_archive(run_info['title'], window, archive=True, clear_selected=True)
        if hide_archived:
            run_info = {}
            run_info = update_run_list(window, run_info, hide_archived=hide_archived)
        else:
            run_info = update_run_list(window, run_info, run_to_select=run_info['title'], hide_archived=hide_archived)

    return run_info

def infotab_event(event, run_info, selected_run_title, hide_archived, font, values, window):
    event = event[8:]
    print(event)

    if event == '-VIEW SAMPLES-':
        if 'title' in run_info:
            if 'samples_column' in run_info:
                samples_column = run_info['samples_column']
            else:
                samples_column = None

            if 'barcodes_column' in run_info:
                barcodes_column = run_info['barcodes_column']
            else:
                barcodes_column = None

            try:
                samples = values['-INFOTAB-SAMPLES-']
                parse_window, column_headers = parse_columns_window.create_parse_window(samples, font=font, samples_column=samples_column, barcodes_column=barcodes_column)
                samples_barcodes_indices = parse_columns_window.run_parse_window(parse_window,samples,column_headers)

                if samples_barcodes_indices != None:
                    samples_column, barcodes_column = samples_barcodes_indices
                    run_info['samples'] = samples
                    run_info['barcodes_column'] = barcodes_column
                    run_info['samples_column']  = samples_column
                    view_barcodes_window.save_barcodes(run_info)

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
                run_info = update_run_list(window, run_info, hide_archived=hide_archived)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    elif event == '-ARCHIVE/UNARCHIVE-':
        if 'title' in run_info:
            try:
                run_info = archive_button(run_info, window, values, hide_archived)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    elif event == '-RUN NAME-FocusOut':
        try:
            if 'title' in run_info:
                rename_run(values, run_info, window, hide_archived=hide_archived)
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
                run_info = save_changes(values, run_info, window, hide_archived=hide_archived)
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

    return run_info, selected_run_title
