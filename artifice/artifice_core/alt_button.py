import PySimpleGUI as sg
import base64
from PIL import Image, ImageDraw, ImageFont, ImageTk
from io import BytesIO
from tkinter import ttk

from artifice_core import consts

# Alternative to standard PySimpleGUI button, with curved edges. Highlights on mouseover
# intialise_buttons function must be called
class AltButton(sg.Button):

    def __init__(self, button_text='', size=(None, None), s=(None,None), button_colors=(None, None), mouseover_colors=(None, None), **kwargs):
        theme = consts.get_theme(sg.theme())
    
        self.Font = kwargs['font'] if 'font' in kwargs and kwargs['font'] != None else consts.BUTTON_FONT if consts.BUTTON_FONT else ('Helvetica', '18') #consts ('Helvetica', '18')
        self.ButtonText = button_text
        self.ButtonColor = sg.button_color_to_tuple(theme['BUTTON'])
        self.MouseOverColors = sg.button_color_to_tuple(theme['BUTTON_HOVER'])

        if button_colors != (None, None):
            self.ButtonColor = sg.button_color_to_tuple(button_colors)

        if mouseover_colors != (None, None):
            self.MouseOverColors = sg.button_color_to_tuple(mouseover_colors)

        self.AltColors = (self.ButtonColor[1],self.ButtonColor[0])

        self.Size = size if size != (None, None) else s if s != (None, None) else (None, None)#consts.BUTTON_SIZE
        scaling=consts.SCALING
        if self.Size == (None, None):
            self.Size = self.get_string_size()
            self.Size = (int(self.Size[0]+self.Size[1]*3*scaling), int(self.Size[1]*1.75*scaling))
        else:
            self.Size = (int(self.Size[0]*scaling), int(self.Size[1]*scaling))

        self.RegImage = self.create_button_image(fill=self.ButtonColor[1])
        self.HighlightImage = self.create_button_image(fill=self.MouseOverColors[1])
        self.MouseOverColors = (self.MouseOverColors[0], sg.theme_background_color())

        kwargs['image_data'] = self.RegImage
        kwargs['button_color'] = (sg.theme_background_color(), sg.theme_background_color())
        kwargs['border_width'] = 0

        super().__init__(mouseover_colors=self.MouseOverColors, button_text=self.ButtonText, **kwargs)

    # set text color of button whether it is a ttk (on Mac) or tk button
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
        self.set_text_color(self.AltColors[1])


    # highlight button
    def on_enter(self, e):
        self.update(image_data=self.HighlightImage)
        self.set_text_color(self.AltColors[0])

    # return to normal color scheme
    def on_leave(self, e):
        self.update(image_data=self.RegImage)
        self.set_text_color(self.AltColors[1])

    # determines the size of the string for font size given
    def get_string_size(self):
        try:
            font = ImageFont.truetype('arial.ttf', int(self.Font[1]))
        except:
            try:
                font = ImageFont.truetype('Keyboard.ttf', int(self.Font[1]))
            except:
                font_file = consts.get_resource('./resources/LiberationSans-Regular.ttf')
                font = ImageFont.truetype(font_file, int(self.Font[1]))

        #size = font.getsize(self.ButtonText)
        width = sg.tkinter.font.Font(font=self.Font).measure(self.ButtonText)
        height = font.getsize(f'{self.ButtonText}g')[1]
        size = (width, height)
        return size

    # create image to be used as button icon
    def create_button_image(self, fill='#ff0000'):
        scl_fctr = 4 #amount to scale up by when drawing
        button_image = Image.new("RGBA", (self.Size[0]*scl_fctr,self.Size[1]*scl_fctr), (255, 255, 255, 0))
        draw = ImageDraw.Draw(button_image)
        #draw.rounded_rectangle([(0,0),((self.Size[0])*scl_fctr,self.Size[1]*scl_fctr)], radius=self.Size[1]*scl_fctr, fill=fill)
        draw.rounded_rectangle([(0,0),((self.Size[0])*scl_fctr,self.Size[1]*scl_fctr)], radius=32, fill=fill)
        button_image = button_image.resize(self.Size, resample=Image.BILINEAR) # resize to actual size with antialiasing for smoother shape

        buffered = BytesIO()
        button_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @staticmethod
    # initialise all AltButtons to highlight on mouseover on given window
    # NOTE: window must first be finalized in order for this work
    def intialise_buttons(window):
        for element in window.element_list():
            if isinstance(element, AltButton):
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

# Lazy function for DummyButton based on AltButton, otherqise identical to PySimpleGUI DummyButton
def AltDummyButton(button_text, image_filename=None, image_data=None, image_size=(None, None), image_subsample=None,
                border_width=None, tooltip=None, size=(None, None), s=(None, None), auto_size_button=None, button_color=None, font=None,
                disabled=False, bind_return_key=False, focus=False, pad=None, p=None, key=None, k=None, visible=True, metadata=None):

    return AltButton(button_text=button_text, button_type=sg.BUTTON_TYPE_CLOSES_WIN_ONLY, image_filename=image_filename,
                  image_data=image_data, image_size=image_size, image_subsample=image_subsample,
                  border_width=border_width, tooltip=tooltip, size=size, s=s, auto_size_button=auto_size_button,
                  button_color=button_color, font=font, disabled=disabled, bind_return_key=bind_return_key, focus=focus,
                  pad=pad, p=p, key=key, k=k, visible=visible, metadata=metadata)
