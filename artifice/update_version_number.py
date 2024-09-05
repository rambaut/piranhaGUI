import sys

BASE_PATH = 'artifice/'

def update_version_number(version_number, application_name):
    print(application_name)
    if application_name == 'piranhaGUI':
        # Updating version number in consts file, for displaying the correct version number in artifice itself, and checking for updates
        replace_line(f'{BASE_PATH}artifice_core/consts.py','PIRANHA_GUI_VERSION =',f"PIRANHA_GUI_VERSION = '{version_number}'",encoding='utf8')
    
    update_linux_version_number(version_number, application_name)
    update_mac_version_number(version_number, application_name)
    update_windows_version(version_number,application_name)

def update_linux_version_number(version_number, application_name):
    # Updating for the title of the package file
    with open(f'{BASE_PATH}linux_build/version_number', 'w') as f:
        f.write(f'#!/bin/bash \n\nVERSION_NUMBER={version_number}')
    
    # Updating the Debian package control file
    replace_line(f'{BASE_PATH}linux_build/linux_dist_files/{application_name}/control','Version:',f'Version: {version_number}')

def update_mac_version_number(version_number, application_name):
    # Updating the pyinstaller 
    replace_line(f'{BASE_PATH}mac_build/pyinstaller_build/{application_name}.spec', '    name=',
                  [f"    name='{application_name}v{version_number}',",
                   "    name='artifice',",
                   f"    name='{application_name}v{version_number}.app',"])

def update_windows_version(version_number, application_name):
    # Updating the InnoSetup .iss file
    replace_line(f'{BASE_PATH}windows_build/dist/{application_name}_installer.iss','AppVersion=',f'AppVersion={version_number}')
    replace_line(f'{BASE_PATH}windows_build/dist/{application_name}_installer.iss','OutputBaseFilename=',f'OutputBaseFilename={application_name}v{version_number}_installer_windows')

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
