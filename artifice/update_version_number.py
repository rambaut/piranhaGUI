import sys

def update_version_number(version_number, application_name):
    print(application_name)
    if application_name == 'piranhaGUI':
        # Updating version number in consts file, for displaying the correct version number in artifice itself, and checking for updates
        replace_line(f'artifice_core/consts.py','PIRANHA_GUI_VERSION =',f"PIRANHA_GUI_VERSION = '{version_number}'",encoding='utf8')
    
    update_linux_version_number(version_number, application_name)

def update_linux_version_number(version_number, application_name):
    # Updating for the title of the package file
    with open('linux_build/version_number', 'w') as f:
        f.write(f'#!/bin/bash \n\nVERSION_NUMBER={version_number}')
    
    # Updating the Debian package control file
    replace_line(f'linux_build/linux_dist_files/{application_name}/control','Version:',f'Version: {version_number}')

def update_mac_version_number(version_number, application_name):
    replace_line('mac_build/pyinstaller_build/piranhaGUI.spec', '    name=', ["    name='piranhaGUIv1.5.5',", ])

# helper function to replace lines
def replace_line(filepath, search_string, replace_strings, encoding=None):
    if type(replace_strings) == str:
        replace_strings = [replace_strings]
    with open(filepath, 'r', encoding=encoding) as f:
        lines = f.readlines()
        num_replaced = 0
        for i in range(len(lines)):
            if lines[i].startswith(search_string):
                    if num_replaced <= len(replace_strings):
                        lines[i] = f'{replace_strings[num_replaced]}\n'
                        num_replaced += 1
                    
        data = lines
    
    with open(filepath, 'w',encoding=encoding) as f:
        f.writelines(data)
    
if __name__ == '__main__':
    
    update_version_number(str(sys.argv[1]),str(sys.argv[2]))
