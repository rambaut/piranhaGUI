import PySimpleGUI as sg
from PIL import ImageFont

class AltButton(sg.Button):

    def __init__(self, size=(None, None), s=(None,None), **kwargs):
        sz = size if size != (None, None) else s

        super().__init__(**kwargs)
        #print(self.Font)
        #print(self.get_string_width())

    def get_string_width(self):

        font = ImageFont.truetype('arial.ttf', 11)
        #font = ImageFont.truetype(self.Font)
        size = font.getsize(self.ButtonText)
        return size
