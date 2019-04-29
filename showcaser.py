import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
from transforms import RGBTransform

from beatmaps import get_pool, beatmap


class button:

    def __init__(self, window, map, mod, location=(0,0), width=900):
        
        self.window = window

        self.map = map
        self.mod = mod

        self.location = location
        self.image_size = width

        self.image = Image.open(self.map.image_path)
        
        self.ratio = self.image_size / self.image.size[0]

        self.image = self.resize_image(self.image)
        self.show_image = ImageTk.PhotoImage(self.image)

        self.state = 0

        self.button = tk.Button ( self.window, bd = 0, image=self.show_image, command=self.change_color) 
        self.button.grid(row = self.location[0], column = self.location[1])

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

        self.button.configure(image=self.show_image)
        self.button.image = self.show_image
    

class window:

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


            
        
        
        

'''

shit = window()

shit.parse_buttons()


'''

top = tk.Tk()

top.geometry("1420x530")

my_map = beatmap("176960")

my_button = button(top, my_map, "nm",(0,0) ,400)
my_button2 = button(top, my_map, "nm",(1,0) , 400)
my_button3 = button(top, my_map, "nm",(2,0) , 400)
my_button4 = button(top, my_map, "nm",(3,0) , 400)
my_button5 = button(top, my_map, "nm",(4,0) , 400)
my_button6 = button(top, my_map, "nm",(5,0) , 400)
my_button7 = button(top, my_map, "nm",(0,1) , 400)
my_button8 = button(top, my_map, "nm",(0,2) , 400)



top.mainloop()


