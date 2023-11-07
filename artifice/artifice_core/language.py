import csv
import artifice_core.consts as consts
from os import path
from artifice_core.update_log import update_log

def get_translate_scheme(filepath = './resources/translation_scheme.csv'):
    filepath = consts.get_resource(filepath)
    with open(filepath, newline = '', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        scheme_list = list(csvreader)

    return scheme_list

# Takes text (in english) and returns version in given language if translation in scheme
def translate_text(string: str, language: str, scheme_list = None, append_scheme = True, vb = False):
    if scheme_list == None or append_scheme:
        scheme_list = get_translate_scheme()

    languages = scheme_list[0]
    lang_pos = 0
    for lang in languages:
        if lang == language:
            lang_pos = languages.index(language)

    return_string = string # if no translation exists, the given string is returned back
    string_in_scheme = False
    try:
        for row in scheme_list:
            if string == row[0]:
                string_in_scheme = True
                try:
                    if row[lang_pos] != '':
                        return_string = row[lang_pos]
                        break
                    else:
                        break
                except:
                    break

        if append_scheme:
            if not string_in_scheme:
                scheme_list.append([string,])
                with open('./resources/translation_scheme.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    for row in scheme_list:
                        csvwriter.writerow(row)
    except Exception as err:
        update_log(f'failed to translate string:')
        update_log(err)
        return_string = string
        print(string)

    if vb: # for debugging
        print(language)
        print(return_string)

    return return_string

def setup_translator():
    config = consts.retrieve_config()
    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'
        
    return lambda text : translate_text(text, language, translate_scheme)

translator = setup_translator()

