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
def translate_text(string: str, language: str, scheme_list = None, append_scheme = True, multi_line_fix = True, #<- splits translated string if there's multiple lines
                    vb = False):
    if scheme_list == None or append_scheme:
        scheme_list = get_translate_scheme()

    languages = scheme_list[0]
    lang_pos = 0
    for lang in languages:
        if lang == language:
            lang_pos = languages.index(language)
    if lang_pos == 0:
        return string #return string if language is default (english)

    return_string = string # if no translation exists, the given string is returned back

    multi_line = False
    if '\n' in string:
        multi_line = True
        lines = string.split('\n')
        string = string.replace('\n', ' ')

    string_in_scheme = False
    try:
        for row in scheme_list:
            try:
                this_row = row[0]
            except:
                break
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
                
        if string_in_scheme:
            if multi_line_fix:
                if multi_line:
                    translated_words = return_string.split(' ')
                    return_string = ''
                    return_line = ''
                    max_len = 0
                    for line in lines:
                        if len(line) > max_len:
                            max_len = len(line)

                    while len(translated_words) > 0:
                        if len(return_line) + len(translated_words[0]) <= max_len or len(return_line) == 0:
                            word = translated_words.pop(0)
                            return_line += word + ' '
                        else:
                            return_line = return_line[:-1]
                            return_string += '\n' + return_line
                            return_line = ''
                    return_line = return_line[:-1]
                    return_string += '\n' + return_line


        if append_scheme:
            if not string_in_scheme:
                scheme_list.append([string,''])
                with open('./resources/translation_scheme.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    for row in scheme_list:
                        csvwriter.writerow(row)

    except Exception as err:
        update_log(f'failed to translate string: {string}')
        update_log(err)
        return_string = string

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

