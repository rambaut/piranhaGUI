import PySimpleGUI as sg
import base64
from PIL import Image, ImageDraw, ImageFont, ImageTk
from io import BytesIO

class AltButton(sg.Button):

    def __init__(self, size=(None, None), s=(None,None), **kwargs):
        self.Font = kwargs['font'] if 'font' in kwargs else sg.DEFAULT_FONT
        self.ButtonText = kwargs['button_text'] if 'button_text' in kwargs else ''

        self.Size = size if size != (None, None) else s
        if self.Size == (None, None):
            #width = int(self.get_string_size()
            #print(width)
            self.Size = self.get_string_size()
            self.Size = (self.Size[0]+self.Size[1]*3, self.Size[1]*2)
            #self.Size = tuple([3*x for x in self.Size])

        #kwargs['image_filename']='./resources/button.png'


        #self
        self.RegImage = self.create_button_image(fill=sg.theme_button_color()[1])
        self.PressImage = self.create_button_image(fill=sg.theme_button_color()[0])

        kwargs['image_data'] = self.RegImage
        kwargs['button_color'] = (sg.theme_background_color(), sg.theme_background_color())
        kwargs['border_width'] = 0

        super().__init__(**kwargs)


    def bind_mouseover(self):
        self.Widget.bind("<Enter>", self.on_enter)
        self.Widget.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.update(image_data=self.PressImage)

    def on_leave(self, e):
        self.update(image_data=self.RegImage)


    def get_string_size(self):

        #font = ImageFont.truetype('arial.ttf', 18)
        font = ImageFont.truetype('arial.ttf', self.Font[1])
        size = font.getsize(self.ButtonText)
        return size

    def create_button_image(self,  fill='#ff0000'):
        button_image = Image.new("RGBA", self.Size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(button_image)
        draw.rounded_rectangle([(0,0),self.Size], radius=self.Size[1], fill=fill)

        buffered = BytesIO()
        button_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    def ButtonPressCallBack(self, parm):
        self.update(image_data=self.PressImage)
        super().ButtonPressCallBack(parm)

    """
    def ButtonCallBack(self):
        self.update(image_data=self.PressImage)
        super().ButtonCallBack()
"""

    def ButtonReleaseCallBack(self):
        super().ButtonReleaseCallBack()
        self.update(image_data=self.PressImage)
