import file_explorer
import config_window

if __name__ == '__main__':

    window = file_explorer.create_explorer_window()
    filenames = file_explorer.run_explorer_window(window)
    print(filenames)

    window = config_window.create_config_window(filenames)
    config_window.run_config_window(window)


    window.close()
