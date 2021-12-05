import selection_window

def create_run():
    window = selection_window.create_select_window()
    samples, MinKnow = selection_window.run_select_window(window)
