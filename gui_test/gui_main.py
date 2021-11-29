import file_explorer
import config_window
#runs the file explorer, once the user selects their files opens the config window and passes on the files

if __name__ == '__main__':

    window = file_explorer.create_explorer_window()
    filenames = file_explorer.run_explorer_window(window)

    if filenames != None:
        window = config_window.create_config_window(filenames)
        config_window.run_config_window(window, filenames)


    window.close()
