import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageOps
import math
import numpy as np
from transforms import RGBTransform

from beatmaps import get_pool, Beatmap


class Button:

    def __init__(self, window, map, mod, location=(0,0), width=900, mask=None):
        
        self.window = window

        self.map = map
        self.mod = mod

        self.location = location
        self.image_size = width

        self.image = Image.open(self.map.image_path)
        
        self.ratio = self.image_size / self.image.size[0]

        self.image = self.resize_image(self.image)

        self.image.paste(mask, mask=mask)

        self.show_image = ImageTk.PhotoImage(self.image)

        self.state = 0

        self.clickable = tk.Button (self.window, bd = 0, image=self.show_image, command=self.change_color)
        self.clickable.grid(row = self.location[0], column = self.location[1])

    def resize_image(self, image):
        
        width = self.ratio * image.size[0]
        height = self.ratio * image.size[1]

        image = image.resize((int(width),int(height)), Image.ANTIALIAS)
        return image

    def put_info(self, image):

        pass

    def change_color(self):

        if self.state == 0:
            #change from normal to black for bans
            temp_image = RGBTransform().mix_with((0, 0, 0),factor=0.6).applied_to(self.image)
            self.state +=1

        elif self.state == 1:
            #change from black to red for pick
            temp_image = RGBTransform().mix_with((255, 0, 0),factor=0.3).applied_to(self.image)
            self.state +=1
        
        elif self.state == 2:
            #change from red to blue for pick
            temp_image = RGBTransform().mix_with((0, 0, 255),factor=0.3).applied_to(self.image)
            self.state +=1

        elif self.state == 3:
            #change from blue to normal for reset
            temp_image = self.image
            self.state = 0 

        self.show_image = ImageTk.PhotoImage(temp_image)

        self.clickable.configure(image=self.show_image)
        self.clickable.image = self.show_image
    

class Window:

    def __init__(self, window_size=(1420, 530) ):

        self.pool = get_pool()
        self.window_size = window_size
        
        self.button_list = []

    def parse_buttons(self, max_col = 3, horizontal_space_ratio = 0.2, vertical_space_ratio = 0.2):
        
        rows = []
        for mod,maps in self.pool.items():

            row_count = int(len(maps)/max_col)

            for row in range(row_count):
                rows.append([mod,maps[row*max_col:(row+1)*max_col]] )

            if len(maps)%max_col != 0 and row_count !=0:
                rows.append( [mod,maps[(row+1)*max_col:]] )

            elif row_count == 0:
                rows.append( [mod,maps] )


def rounded_rectangle(draw, xy, rad, fill=None):
    x0, y0, x1, y1 = xy
    draw.rectangle([ (x0, y0 + rad), (x1, y1 - rad) ], fill=fill)
    draw.rectangle([ (x0 + rad, y0), (x1 - rad, y1) ], fill=fill)
    draw.pieslice([ (x0, y0), (x0 + rad * 2, y0 + rad * 2) ], 180, 270, fill=fill)
    draw.pieslice([ (x1 - rad * 2, y1 - rad * 2), (x1, y1) ], 0, 90, fill=fill)
    draw.pieslice([ (x0, y1 - rad * 2), (x0 + rad * 2, y1) ], 90, 180, fill=fill)
    draw.pieslice([ (x1 - rad * 2, y0), (x1, y0 + rad * 2) ], 270, 360, fill=fill)


top = tk.Tk()

top.geometry("1420x530")

cover_size = 400


# Rounded Rectangular Mask
mask = Image.new('L', (cover_size, cover_size*250//900), 0)
draw = ImageDraw.Draw(mask)
rounded_rectangle(draw, (0, 0, cover_size, cover_size*250//900), rad=40, fill=255)
mask = ImageOps.invert(mask)
#mask.show()

# Map ids, in an array
maps = ["176960", "2002882", "1996791", "2004799", "1994939", "2005243",
        "1950850", "1917673", "1555061", "1997180", "2006468"]

# Map objects as beatmap class
my_map = [Beatmap(idx) for idx in maps]

# For all beatmaps, create a button
for buttonNo in range(len(maps)):
    Button(top, my_map[buttonNo], "nm", (buttonNo % 5, math.floor(buttonNo / 5)), cover_size, mask=mask)

top.mainloop()


