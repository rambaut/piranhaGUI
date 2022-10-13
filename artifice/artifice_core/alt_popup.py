import PySimpleGUI as sg
import textwrap

from artifice_core.alt_button import AltButton, AltDummyButton

# function that creates popup with AltButtons, otherwise identical to PySimpleGUI popup
# Modified lines have been marked #EDITED, it may be wise to copy popup() if it is updated in future and if using PySimpleGUI beyond v4.60
# This is seems messy to me but I can't think of another way of doing this
def alt_popup(*args, title=None, button_color=None, background_color=None, text_color=None, button_type=sg.POPUP_BUTTONS_OK, auto_close=False,
          auto_close_duration=None, custom_text=(None, None), non_blocking=False, icon=None, line_width=None, font=None, no_titlebar=False, grab_anywhere=False,
          keep_on_top=None, location=(None, None), relative_location=(None, None), any_key_closes=False, image=None, modal=True):
    """
    Popup - Display a popup Window with as many parms as you wish to include.  This is the GUI equivalent of the
    "print" statement.  It's also great for "pausing" your program's flow until the user can read some error messages.

    If this popup doesn't have the features you want, then you can easily make your own. Popups can be accomplished in 1 line of code:
    choice, _ = sg.Window('Continue?', [[sg.T('Do you want to continue?')], [sg.Yes(s=10), sg.No(s=10)]], disable_close=True).read(close=True)


    :param *args:               Variable number of your arguments.  Load up the call with stuff to see!
    :type *args:                (Any)
    :param title:               Optional title for the window. If none provided, the first arg will be used instead.
    :type title:                (str)
    :param button_color:        Color of the buttons shown (text color, button color)
    :type button_color:         (str, str) | None
    :param background_color:    Window's background color
    :type background_color:     (str)
    :param text_color:          text color
    :type text_color:           (str)
    :param button_type:         NOT USER SET!  Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK). There are many Popup functions and they call Popup, changing this parameter to get the desired effect.
    :type button_type:          (int)
    :param auto_close:          If True the window will automatically close
    :type auto_close:           (bool)
    :param auto_close_duration: time in seconds to keep window open before closing it automatically
    :type auto_close_duration:  (int)
    :param custom_text:         A string or pair of strings that contain the text to display on the buttons
    :type custom_text:          (str, str) | str
    :param non_blocking:        If True then will immediately return from the function without waiting for the user's input.
    :type non_blocking:         (bool)
    :param icon:                icon to display on the window. Same format as a Window call
    :type icon:                 str | bytes
    :param line_width:          Width of lines in characters.  Defaults to MESSAGE_BOX_LINE_WIDTH
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 str | Tuple[font_name, size, modifiers]
    :param no_titlebar:         If True will not show the frame around the window and the titlebar across the top
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True can grab anywhere to move the window. If no_titlebar is True, grab_anywhere should likely be enabled too
    :type grab_anywhere:        (bool)
    :param location:            Location on screen to display the top left corner of window. Defaults to window centered on screen
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param any_key_closes:      If True then will turn on return_keyboard_events for the window which will cause window to close as soon as any key is pressed.  Normally the return key only will close the window.  Default is false.
    :type any_key_closes:       (bool)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None
    """

    if not args:
        args_to_print = ['']
    else:
        args_to_print = args
    if line_width != None:
        local_line_width = line_width
    else:
        local_line_width = sg.MESSAGE_BOX_LINE_WIDTH #EDITED to put sg.
    _title = title if title is not None else args_to_print[0]

    layout = [[]]
    max_line_total, total_lines = 0, 0
    if image is not None:
        if isinstance(image, str):
            layout += [[sg.Image(filename=image)]] #EDITED to put sg.
        else:
            layout += [[sg.Image(data=image)]] #EDITED to put sg.

    for message in args_to_print:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        if message.count('\n'):  # if there are line breaks, then wrap each segment separately
            # message_wrapped = message         # used to just do this, but now breaking into smaller pieces
            message_wrapped = ''
            msg_list = message.split('\n')  # break into segments that will each be wrapped
            message_wrapped = '\n'.join([textwrap.fill(msg, local_line_width) for msg in msg_list])
        else:
            message_wrapped = textwrap.fill(message, local_line_width)
        message_wrapped_lines = message_wrapped.count('\n') + 1
        longest_line_len = max([len(l) for l in message.split('\n')])
        width_used = min(longest_line_len, local_line_width)
        max_line_total = max(max_line_total, width_used)
        # height = _GetNumLinesNeeded(message, width_used)
        height = message_wrapped_lines
        layout += [[
            sg.Text(message_wrapped, auto_size_text=True, text_color=text_color, background_color=background_color)]]
        total_lines += height

    if non_blocking:
        PopupButton = AltDummyButton  # important to use or else button will close other windows too! #EDITED to be AltButton
    else:
        PopupButton = AltButton #EDITED to be AltButton
    # show either an OK or Yes/No depending on paramater
    if custom_text != (None, None):
        if type(custom_text) is not tuple:
            layout += [[PopupButton(custom_text, button_color=button_color, focus=True, #EDITED removed size argument
                                    bind_return_key=True,font=font),]] #EDITED include font argument
        elif custom_text[1] is None:
            layout += [[
                PopupButton(custom_text[0], button_color=button_color, focus=True,
                            bind_return_key=True,font=font)]] #EDITED include font argument removed size argument
        else:
            layout += [[PopupButton(custom_text[0], button_color=button_color, focus=True, bind_return_key=True,
                                    font=font), #EDITED removed size argument
                        PopupButton(custom_text[1], button_color=button_color,font=font)]] #EDITED include font argument removed size argument
    elif button_type is sg.POPUP_BUTTONS_YES_NO: #EDITED to put sg.
        layout += [[PopupButton('Yes', button_color=button_color, focus=True, bind_return_key=True, pad=((20, 5), 3),
                                font=font), PopupButton('No', button_color=button_color,font=font)]] #EDITED include font argument removed size argument
    elif button_type is sg.POPUP_BUTTONS_CANCELLED: #EDITED to put sg.
        layout += [[
            PopupButton('Cancelled', button_color=button_color, focus=True, bind_return_key=True, pad=((20, 0), 3),font=font)]] #EDITED include font argument
    elif button_type is sg.POPUP_BUTTONS_ERROR: #EDITED to put sg.
        layout += [[PopupButton('Error', button_color=button_color, focus=True, bind_return_key=True,
                                pad=((20, 0), 3),font=font)]] #EDITED include font argument removed size argument
    elif button_type is sg.POPUP_BUTTONS_OK_CANCEL: #EDITED to put sg.
        layout += [[PopupButton('OK', button_color=button_color, focus=True, bind_return_key=True,font=font), #EDITED include font argument removed size argument
                    PopupButton('Cancel', button_color=button_color,font=font)]] #EDITED include font argument removed size argument
    elif button_type is sg.POPUP_BUTTONS_NO_BUTTONS: #EDITED to put sg.
        pass
    else:
        layout += [[PopupButton('OK', button_color=button_color, focus=True, bind_return_key=True, #EDITED removed size argument
                                pad=((20, 0), 3),font=font)]] #EDITED include font argumen

    window = sg.Window(_title, layout, auto_size_text=True, background_color=background_color, button_color=button_color, #EDITED to put sg.
                    auto_close=auto_close, auto_close_duration=auto_close_duration, icon=icon, font=font, #EDITED include font argumen
                    no_titlebar=no_titlebar, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location, relative_location=relative_location, return_keyboard_events=any_key_closes,
                    modal=modal, finalize=True) #EDITED added finalize

    AltButton.intialise_buttons(window)
    if non_blocking:
        button, values = window.read(timeout=0)
    else:
        button, values = window.read()
        window.close()
        del window

    return button

# lazy function to create popup_ok, identical to PySimpleGUI popup_ok but uses alt_buttons
def alt_popup_ok(*args, title=None, button_color=None, background_color=None, text_color=None, auto_close=False,
             auto_close_duration=None, non_blocking=False, icon=None, line_width=None, font=None,
             no_titlebar=False, grab_anywhere=False, keep_on_top=None, location=(None, None), relative_location=(None, None), image=None, modal=True):
    """
    Display Popup with OK button only

    :param *args:               Variable number of items to display
    :type *args:                (Any)
    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) or str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype:                     str | None | TIMEOUT_KEY
    """
    return alt_popup(*args, title=title, button_type=sg.POPUP_BUTTONS_OK, background_color=background_color, text_color=text_color, #EDITED to put sg.
                 non_blocking=non_blocking, icon=icon, line_width=line_width, button_color=button_color, auto_close=auto_close,
                 auto_close_duration=auto_close_duration, font=font, no_titlebar=no_titlebar, grab_anywhere=grab_anywhere,
                 keep_on_top=keep_on_top, location=location, relative_location=relative_location, image=image, modal=modal)

# lazy function to create popup_yes_no, identical to PySimpleGUI popup_yes_no but uses alt_buttons
def alt_popup_yes_no(*args, title=None, button_color=None, background_color=None, text_color=None, auto_close=False,
                 auto_close_duration=None, non_blocking=False, icon=None, line_width=None, font=None,
                 no_titlebar=False, grab_anywhere=False, keep_on_top=None, location=(None, None), relative_location=(None, None), image=None, modal=True):
    """
    Display Popup with Yes and No buttons

    :param *args:               Variable number of items to display
    :type *args:                (Any)
    :param title:               Title to display in the window.
    :type title:                (str)
    :param button_color:        button color (foreground, background)
    :type button_color:         (str, str) or str
    :param background_color:    color of background
    :type background_color:     (str)
    :param text_color:          color of the text
    :type text_color:           (str)
    :param auto_close:          if True window will close itself
    :type auto_close:           (bool)
    :param auto_close_duration: Older versions only accept int. Time in seconds until window will close
    :type auto_close_duration:  int | float
    :param non_blocking:        if True the call will immediately return rather than waiting on user input
    :type non_blocking:         (bool)
    :param icon:                filename or base64 string to be used for the window's icon
    :type icon:                 bytes | str
    :param line_width:          Width of lines in characters
    :type line_width:           (int)
    :param font:                specifies the  font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    :type font:                 (str or (str, int[, str]) or None)
    :param no_titlebar:         If True no titlebar will be shown
    :type no_titlebar:          (bool)
    :param grab_anywhere:       If True: can grab anywhere to move the window (Default = False)
    :type grab_anywhere:        (bool)
    :param keep_on_top:         If True the window will remain above all current windows
    :type keep_on_top:          (bool)
    :param location:            Location of upper left corner of the window
    :type location:             (int, int)
    :param relative_location:   (x,y) location relative to the default location of the window, in pixels. Normally the window centers.  This location is relative to the location the window would be created. Note they can be negative.
    :type relative_location:    (int, int)
    :param image:               Image to include at the top of the popup window
    :type image:                (str) or (bytes)
    :param modal:               If True then makes the popup will behave like a Modal window... all other windows are non-operational until this one is closed. Default = True
    :type modal:                bool
    :return:                    clicked button
    :rtype:                     "Yes" | "No" | None
    """
    return alt_popup(*args, title=title, button_type=sg.POPUP_BUTTONS_YES_NO, background_color=background_color,
                 text_color=text_color,
                 non_blocking=non_blocking, icon=icon, line_width=line_width, button_color=button_color,
                 auto_close=auto_close, auto_close_duration=auto_close_duration, font=font, no_titlebar=no_titlebar,
                 grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location, relative_location=relative_location, image=image, modal=modal)
