import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageOps
import math
import numpy as np
from transforms import RGBTransform
from pathlib import Path

from beatmaps import get_pool, Beatmap


class Button:

    def __init__(self, window, map, mod, location=(0,0), width=900):
        
        self.window = window

        self.map = map
        self.mod = mod

        self.location = location

        self.image = Image.open(self.map.image_path)

        self.width = width
        self.height = int(self.image.size[1] * width / self.image.size[0])

        self.image = self.resize_image(self.image, self.width)
        self.add_mask(self.image)
        self.show_image = ImageTk.PhotoImage(self.image)

        self.mod_image = self.load_mod()
        self.mod_image = self.resize_image(self.mod_image, width//2)
        self.paste_mod(self.image)

        self.show_image = ImageTk.PhotoImage(self.image)

        self.state = 0

        self.clickable = tk.Button (self.window, bd = 0, image=self.show_image, command=self.change_color, borderwidth=0, highlightthickness = 0)
        self.clickable.grid(row = self.location[0], column = self.location[1])

    def resize_image(self, image, width):
        
        ratio = width / self.image.size[0]
        
        width = int(ratio * image.size[0])
        height = int(ratio * image.size[1])

        image = image.resize((width, height), Image.ANTIALIAS)
        return image
    
     
    def rounded_rectangle(self, draw, xy, rad, fill=None):
        
        x0, y0, x1, y1 = xy
        draw.rectangle([ (x0, y0 + rad), (x1, y1 - rad) ], fill=fill)
        draw.rectangle([ (x0 + rad, y0), (x1 - rad, y1) ], fill=fill)
        draw.pieslice([ (x0, y0), (x0 + rad * 2, y0 + rad * 2) ], 180, 270, fill=fill)
        draw.pieslice([ (x1 - rad * 2, y1 - rad * 2), (x1, y1) ], 0, 90, fill=fill)
        draw.pieslice([ (x0, y1 - rad * 2), (x0 + rad * 2, y1) ], 90, 180, fill=fill)
        draw.pieslice([ (x1 - rad * 2, y0), (x1, y0 + rad * 2) ], 270, 360, fill=fill)
    
    
    def add_mask(self, image):

        # Rounded Rectangular Mask
        self.mask = Image.new('L', (self.width, self.height), 0)
        self.draw = ImageDraw.Draw(self.mask)
        self.rounded_rectangle(self.draw, (0, 0, self.width, self.height), rad=40, fill=255)
        self.mask = ImageOps.invert(self.mask)
        image.paste(self.mask, mask=self.mask)

    
    def load_mod(self):
        
        folder_dir = Path("mods")

        if self.mod == "No Mod":
            image_name = "selection-mod-Nomod@2x"
        elif self.mod == "Hidden":
            image_name = "selection-mod-hidden@2x"
        elif self.mod == "Hard Rock":
            image_name = "selection-mod-hardrock@2x"
        elif self.mod == "Double Time":
            image_name = "selection-mod-doubletime@2x"
        elif self.mod == "Free Mod":
            image_name = "selection-mode-Freemod@2x"
        elif self.mod == "Tie Breaker":
            image_name = "selection-mode-Tiebreaker@2x"

        return Image.open(str(folder_dir / image_name) + ".png")
    

    def paste_mod(self, image):
        
        x = (self.width - self.mod_image.size[0]) // 12 
        y = (self.height - self.mod_image.size[1]) // 2

        image.paste(self.mod_image, (x,y), mask = self.mod_image)


    def change_color(self):

        if self.state == 0:
            #change from normal to black for bans
            temp_image = RGBTransform().mix_with((0, 0, 0),factor=0.6).applied_to(self.image)
            self.state +=1

        elif self.state == 1:
            #change from black to red for pick
            temp_image = RGBTransform().mix_with((255, 0, 0),factor=0.4).applied_to(self.image)
            self.state +=1
        
        elif self.state == 2:
            #change from red to blue for pick
            temp_image = RGBTransform().mix_with((0, 0, 255),factor=0.3).applied_to(self.image)
            self.state +=1

        elif self.state == 3:
            #change from blue to normal for reset
            temp_image = self.image
            self.state = 0 

        self.add_mask(temp_image)
        self.paste_mod(temp_image)
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




top = tk.Tk()

top.geometry("1420x530")
top.configure(bg="white")
cover_size = 350


# Map ids, in an array
buttonNo = 0
map_list = []
for mod,maps in get_pool().items():

    for map in maps:
        
        map = Beatmap(map)

        Button(top, map, mod, (buttonNo % 5, math.floor(buttonNo / 5)), cover_size)
        buttonNo += 1


top.mainloop()


