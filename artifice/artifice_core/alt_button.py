import PySimpleGUI as sg
import base64
from PIL import Image, ImageDraw, ImageFont, ImageTk
from io import BytesIO

import artifice_core.consts

class AltButton(sg.Button):

    def __init__(self, size=(None, None), s=(None,None), button_color=None, mouseover_colors=(None, None), **kwargs):
        self.Font = kwargs['font'] if 'font' in kwargs else sg.DEFAULT_FONT
        self.ButtonText = kwargs['button_text'] if 'button_text' in kwargs else ''
        self.ButtonColor = sg.button_color_to_tuple(button_color)

        self.Size = size if size != (None, None) else s
        if self.Size == (None, None):
            #width = int(self.get_string_size()
            #print(width)
            self.Size = self.get_string_size()
            config = artifice_core.consts.retrieve_config()
            scaling=config['SCALING']
            self.Size = (int(self.Size[0]+self.Size[1]*3*scaling), int(self.Size[1]*1.75*scaling))
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


    def bind_mouseover(self):
        self.Widget.bind("<Enter>", self.on_enter)
        self.Widget.bind("<Leave>", self.on_leave)
        self.Widget.config(fg=self.MouseOverColors[1])

    def on_enter(self, e):
        self.update(image_data=self.PressImage)
        self.Widget.config(fg=self.MouseOverColors[0])

    def on_leave(self, e):
        self.update(image_data=self.RegImage)
        self.Widget.config(fg=self.MouseOverColors[1])


    def get_string_size(self):
        #font = ImageFont.truetype('arial.ttf', 18)
        font = ImageFont.truetype('arial.ttf', self.Font[1])
        size = font.getsize(self.ButtonText)
        height = font.getsize(f'{self.ButtonText}g')[1]
        size = (size[0], height)
        return size

    def create_button_image(self, scaling = 1, fill='#ff0000'):
        button_image = Image.new("RGBA", self.Size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(button_image)
        draw.rounded_rectangle([(0,0),self.Size], radius=self.Size[1], fill=fill)

        buffered = BytesIO()
        button_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())
