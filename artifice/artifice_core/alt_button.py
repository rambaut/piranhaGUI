import PySimpleGUI as sg
import base64
from PIL import Image, ImageDraw, ImageFont, ImageTk
from io import BytesIO
from tkinter import ttk

import artifice_core.consts

# Alternative to standard PySimpleGUI button with curved edges. Highlights on mouseover
class AltButton(sg.Button):

    def __init__(self, size=(None, None), s=(None,None), button_color=None, mouseover_colors=(None, None), **kwargs):
        self.Font = kwargs['font'] if 'font' in kwargs else ('Arial', '18')
        self.ButtonText = kwargs['button_text'] if 'button_text' in kwargs else ''
        self.ButtonColor = sg.button_color_to_tuple(button_color)

        self.Size = size if size != (None, None) else s
        config = artifice_core.consts.retrieve_config()
        scaling=config['SCALING']
        if self.Size == (None, None):
            #width = int(self.get_string_size()
            #print(width)
            self.Size = self.get_string_size()
            self.Size = (int(self.Size[0]+self.Size[1]*3*scaling), int(self.Size[1]*1.75*scaling))
        else:
            self.Size = (int(self.Size[0]*scaling), int(self.Size[1]*scaling))
            #self.Size = tuple([3*x for x in self.Size])

        #kwargs['image_filename']='./resources/button.png'

        if mouseover_colors != (None, None):
            self.MouseOverColors = sg.button_color_to_tuple(mouseover_colors)
        elif button_color != None:
            self.MouseOverColors = (self.ButtonColor[1], self.ButtonColor[0])
        else:
            self.MouseOverColors = (sg.theme_button_color()[1], sg.theme_button_color()[0])

        self.RegImage = self.create_button_image(fill=self.MouseOverColors[0])
        self.PressImage = self.create_button_image(fill=self.MouseOverColors[1])

        kwargs['image_data'] = self.RegImage
        kwargs['button_color'] = (sg.theme_background_color(), sg.theme_background_color())
        kwargs['border_width'] = 0

        super().__init__(mouseover_colors=self.MouseOverColors, **kwargs)

    def set_text_color(self, color):
        try:
            alt_style = ttk.Style()
            alt_style.configure(self.Widget.cget('style'), foreground=color)
            #self.Widget.config(style=self.Widget.cget('style'))
        except:
            self.Widget.config(fg=color)

    # bind mouseover events to button, window must be finalized first
    def bind_mouseover(self):
        self.Widget.bind("<Enter>", self.on_enter)
        self.Widget.bind("<Leave>", self.on_leave)
        self.set_text_color(self.MouseOverColors[1])


    # highlight button
    def on_enter(self, e):
        self.update(image_data=self.PressImage)
        self.set_text_color(self.MouseOverColors[0])
        #self.Widget.config(fg=self.MouseOverColors[0])

    # return to normal color scheme
    def on_leave(self, e):
        self.update(image_data=self.RegImage)
        self.set_text_color(self.MouseOverColors[1])


    def get_string_size(self):
        #font = ImageFont.truetype('arial.ttf', 18)
        try:
            font = ImageFont.truetype('arial.ttf', self.Font[1])
        except:
            font = ImageFont.truetype('Keyboard.ttf', self.Font[1])

        size = font.getsize(self.ButtonText)
        height = font.getsize(f'{self.ButtonText}g')[1]
        size = (size[0], height)
        return size

    def create_button_image(self, fill='#ff0000'):
        scl_fctr = 4 #amount to scale up by when drawing
        button_image = Image.new("RGBA", (self.Size[0]*scl_fctr,self.Size[1]*scl_fctr), (255, 255, 255, 0))
        draw = ImageDraw.Draw(button_image)
        draw.rounded_rectangle([(0,0),((self.Size[0]-5)*scl_fctr,self.Size[1]*scl_fctr)], radius=self.Size[1]*scl_fctr, fill=fill)
        button_image = button_image.resize(self.Size, resample=Image.ANTIALIAS) # resize to actual size with antialiasing for smoother shape

        buffered = BytesIO()
        button_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @staticmethod
    # initialise all AltButtons to highlight on mouseover on given window
    # NOTE: window must first be finalized in order for this work
    def intialise_buttons(window):
        for element in window.element_list():
            if hasattr(element, 'bind_mouseover'):
                element.bind_mouseover()

# Lazy function to create AltButton folder browser, consult PySimpleGUI docs for info on parameters
def AltFolderBrowse (button_text='Browse', target=(sg.ThisRow, -1), initial_folder=None, tooltip=None, size=(None, None), s=(None, None),
                 auto_size_button=None, button_color=None, disabled=False, change_submits=False, enable_events=False,
                 font=None, pad=None, p=None, key=None, k=None, visible=True, metadata=None):

                 return AltButton(button_text=button_text, button_type=sg.BUTTON_TYPE_BROWSE_FOLDER, target=target,
                  initial_folder=initial_folder, tooltip=tooltip, size=size, s=s, auto_size_button=auto_size_button,
                  disabled=disabled, button_color=button_color, change_submits=change_submits,
                  enable_events=enable_events, font=font, pad=pad, p=p, key=key, k=k, visible=visible, metadata=metadata)

# Lazy function to create AltButton file browser, consult PySimpleGUI docs for info on parameters
def AltFileBrowse(button_text='Browse', target=(sg.ThisRow, -1), file_types=sg.FILE_TYPES_ALL_FILES, initial_folder=None,
               tooltip=None, size=(None, None), s=(None, None), auto_size_button=None, button_color=None, change_submits=False,
               enable_events=False, font=None, disabled=False,
               pad=None, p=None, key=None, k=None, visible=True, metadata=None):

               return AltButton(button_text=button_text, button_type=sg.BUTTON_TYPE_BROWSE_FILE, target=target, file_types=file_types,
                  initial_folder=initial_folder, tooltip=tooltip, size=size, s=s, auto_size_button=auto_size_button,
                  change_submits=change_submits, enable_events=enable_events, disabled=disabled,
                  button_color=button_color, font=font, pad=pad, p=p, key=key, k=k, visible=visible, metadata=metadata)
