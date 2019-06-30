import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageOps, ImageFilter, ImageFont
import textwrap
import math
import numpy as np
from transforms import RGBTransform
from pathlib import Path

from beatmaps import get_pool, Beatmap


class Button:

    def __init__(self, window, map, mod, location=(0, 0), width=900, padx=0, pady=0):

        self.window = window

        self.map = map
        self.mod = mod
        self.mod_color_dict = {"No Mod": (217,217,217),
                               "Hidden": (255,229,153),
                               "Hard Rock": (234,153,153),
                               "Double Time": (180,167,214),
                               "Free Mod": (182,215,168),
                               "Tie Breaker": (241,194,50)}

        self.mod_hex_dict = {"No Mod": '#d9d9d9',
                             "Hidden": '#ffe599',
                             "Hard Rock": '#ea9999',
                             "Double Time": '#b4a7d6',
                             "Free Mod": '#b6d7a8',
                             "Tie Breaker": '#f1c232'}

        self.location = location

        self.image = Image.open(self.map.image_path)
        self.font = ImageFont.truetype("Bebas-Regular.ttf", size=22)

        self.width = width
        self.height = int(self.image.size[1] * width / self.image.size[0])

        self.image = self.resize_image(self.image, self.width)
        self.add_mask(self.image)
        self.blur_edges(self.image)
        self.show_image = ImageTk.PhotoImage(self.image)

        self.mod_image = self.load_mod()
        self.mod_image = self.resize_image(self.mod_image, width // 3)
        self.add_mod(self.image)
        self.add_text(self.image, (255,255,255))

        self.show_image = ImageTk.PhotoImage(self.image)

        self.state = 0

        self.button_color = self.mod_hex_dict[self.mod]
        self.clickable = tk.Button(self.window, bd=0, image=self.show_image, command=self.change_color,
                                   highlightthickness=0, bg=self.button_color, fg=self.button_color,
                                   activebackground=self.button_color)
        self.clickable.place(x=padx, y=pady, relx=self.location[0], rely=self.location[1], anchor="nw")
        # self.clickable.grid(row=self.location[0], column=self.location[1], padx=padx, pady=pady)

    def resize_image(self, image, width):

        ratio = width / self.image.size[0]

        width = int(ratio * image.size[0])
        height = int(ratio * image.size[1])

        image = image.resize((width, height), Image.ANTIALIAS)
        return image

    def rounded_rectangle(self, draw, xy, rad, fill=None):

        x0, y0, x1, y1 = xy
        draw.rectangle([(x0, y0 + rad), (x1, y1 - rad)], fill=fill)
        draw.rectangle([(x0 + rad, y0), (x1 - rad, y1)], fill=fill)
        draw.pieslice([(x0, y0), (x0 + rad * 2, y0 + rad * 2)], 180, 270, fill=fill)
        draw.pieslice([(x1 - rad * 2, y1 - rad * 2), (x1, y1)], 0, 90, fill=fill)
        draw.pieslice([(x0, y1 - rad * 2), (x0 + rad * 2, y1)], 90, 180, fill=fill)
        draw.pieslice([(x1 - rad * 2, y0), (x1, y0 + rad * 2)], 270, 360, fill=fill)

    def add_mask(self, image):

        # Rounded Rectangular Mask
        mask = Image.new('L', (self.width, self.height), 0)
        draw = ImageDraw.Draw(mask)
        self.rounded_rectangle(draw, (4, 4, self.width - 4, self.height - 4), rad=40, fill=255)
        mask = ImageOps.invert(mask)

        fill_color = self.mod_color_dict[self.mod]
        fill_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        fill_array[..., 0] = fill_color[0]
        fill_array[..., 1] = fill_color[1]
        fill_array[..., 2] = fill_color[2]
        fill_img = Image.fromarray(fill_array, mode='RGB')

        image.paste(fill_img, mask=mask)

    def blur_edges(self, image):

        mask = Image.new('L', (self.width, self.height), 0)
        draw = ImageDraw.Draw(mask)
        self.rounded_rectangle(draw, (7, 7, self.width - 7, self.height - 7), rad=40, fill=255)
        mask = ImageOps.invert(mask)
        image2 = image.filter(ImageFilter.GaussianBlur(radius=2))
        image.paste(image2, mask=mask)

    def draw_text_with_outline(self, image, pos, text, font ,color = (225, 225, 225)):

        text_x, text_y = pos
        draw = ImageDraw.Draw(image)

        draw.text((text_x - 0.5, text_y - 0.5), text, (0, 0, 0), font=font)
        draw.text((text_x + 0.5, text_y - 0.5), text, (0, 0, 0), font=font)
        draw.text((text_x + 0.5, text_y + 0.5), text, (0, 0, 0), font=font)
        draw.text((text_x - 0.5, text_y + 0.5), text, (0, 0, 0), font=font)
        draw.text((text_x, text_y), text, color, font=font)

    def draw_multiple_line_text(self, image, text, font, text_color, mid_height):

        draw = ImageDraw.Draw(image)
        image_width, image_height = image.size
        y_text = 0
        lines = textwrap.wrap(text, width=20)
        for line in lines:
            line_width, line_height = font.getsize(line)
            y_text += line_height

        y_text_2 = 0
        for line in lines:
            line_width, line_height = font.getsize(line)
            self.draw_text_with_outline(image, (1.5 * self.mod_image.size[0] - 10, mid_height - (y_text/2) + y_text_2 + (line_height/2)),
                                    line, self.font, text_color)
            y_text_2 += line_height


    def add_text(self, image, color):

        # map artist -> {self.map.artist}, map title -> {self.map.title}
        map_name_str = f"{self.map.title}"
        mapper_str = f"Mapper: {self.map.mapper}"
        diff_str = f"Difficulty: {self.map.diff_name}"

        self.draw_multiple_line_text(image, map_name_str, self.font, color, 1.5 * self.mod_image.size[1] / 2)

    def load_mod(self):

        folder_dir = Path("mods")

        if self.mod == "No Mod":
            image_name = "nomod"
        elif self.mod == "Hidden":
            image_name = "Hidden"
        elif self.mod == "Hard Rock":
            image_name = "Hardrock"
        elif self.mod == "Double Time":
            image_name = "doubletime"
        elif self.mod == "Free Mod":
            image_name = "freemod"
        elif self.mod == "Tie Breaker":
            image_name = "Tiebreaker"

        return Image.open(str(folder_dir / image_name) + ".png")

    def add_mod(self, image):

        x = (self.width - self.mod_image.size[0]) // 12
        y = (self.height - self.mod_image.size[1]) // 2

        image.paste(self.mod_image, (x, y), mask=self.mod_image)

    def change_color(self):

        if self.state == 0:
            # change from normal to black for bans
            temp_image = RGBTransform().mix_with((0, 0, 0), factor=0.8).applied_to(self.image)
            self.state += 1

        elif self.state == 1:
            # change from black to red for pick
            temp_image = RGBTransform().mix_with((226,54,48), factor=0.6).applied_to(self.image)
            self.state += 1

        elif self.state == 2:
            # change from red to blue for pick
            temp_image = RGBTransform().mix_with((12,0,255), factor=0.6).applied_to(self.image)
            self.state += 1

        elif self.state == 3:
            # change from blue to normal for reset
            temp_image = self.image
            self.state = 0

        self.add_mask(temp_image)
        self.blur_edges(temp_image)
        self.add_mod(temp_image)
        self.add_text(temp_image, (255,255,255))

        self.show_image = ImageTk.PhotoImage(temp_image)

        self.clickable.configure(image=self.show_image)
        self.clickable.image = self.show_image


top = tk.Tk()

top.geometry("1420x530")
top.configure(bg="white")
cover_size = 300

nomod_color = 217
nomod_arr = np.ones((540, 350)) * nomod_color
nm_img = ImageTk.PhotoImage(image=Image.fromarray(nomod_arr))
nomod_label = tk.Label(top, image=nm_img, bg='#d9d9d9')
nomod_label.place(anchor="nw", x=0)

hd_color = (255,229,153)
hd_arr = np.zeros((530, 350, 3), 'uint8')
hd_arr[..., 0] = hd_color[0]
hd_arr[..., 1] = hd_color[1]
hd_arr[..., 2] = hd_color[2]
hd_img = ImageTk.PhotoImage(image=Image.fromarray(hd_arr, mode='RGB'))
hd_label = tk.Label(top, image=hd_img, bg='#ffe599')
hd_label.place(anchor="nw", x=350)

hr_color = (234,153,153)
hr_arr = np.zeros((530, 350, 3), 'uint8')
hr_arr[..., 0] = hr_color[0]
hr_arr[..., 1] = hr_color[1]
hr_arr[..., 2] = hr_color[2]
hr_img = ImageTk.PhotoImage(image=Image.fromarray(hr_arr, mode='RGB'))
hr_label = tk.Label(top, image=hr_img, bg='#ea9999')
hr_label.place(anchor="nw", y=270, x=350)

dt_color = (180,167,214)
dt_arr = np.zeros((530, 350, 3), 'uint8')
dt_arr[..., 0] = dt_color[0]
dt_arr[..., 1] = dt_color[1]
dt_arr[..., 2] = dt_color[2]
dt_img = ImageTk.PhotoImage(image=Image.fromarray(dt_arr, mode='RGB'))
dt_label = tk.Label(top, image=dt_img, bg='#b4a7d6')
dt_label.place(anchor="nw", x=700)

fm_color = (182,215,168)
fm_arr = np.zeros((530, 350, 3), 'uint8')
fm_arr[..., 0] = fm_color[0]
fm_arr[..., 1] = fm_color[1]
fm_arr[..., 2] = fm_color[2]
fm_img = ImageTk.PhotoImage(image=Image.fromarray(fm_arr, mode='RGB'))
fm_label = tk.Label(top, image=fm_img, bg='#b6d7a8')
fm_label.place(anchor="nw", y=270, x=700)

tb_color = (241,194,50)
tb_arr = np.zeros((530, 450, 3), 'uint8')
tb_arr[..., 0] = tb_color[0]
tb_arr[..., 1] = tb_color[1]
tb_arr[..., 2] = tb_color[2]
tb_img = ImageTk.PhotoImage(image=Image.fromarray(tb_arr, mode='RGB'))
tb_label = tk.Label(top, image=tb_img, bg='#f1c232')
tb_label.place(anchor="nw", y=0, x=1050)

buttonNo = 0

for mod, maps in get_pool().items():

    if mod == "No Mod":
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, no / 6), cover_size, 25, 42)
    elif mod == "Hidden":
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, no / 6), cover_size, 375, 5)
    elif mod == "Hard Rock":
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, (no + 3) / 6), cover_size, 375, 10)
    elif mod == "Double Time":
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, no / 6), cover_size, 725, 5)
    elif mod == "Free Mod":
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, (no + 3) / 6), cover_size, 725, 10)
    else:
        for no, map in enumerate(maps):
            map = Beatmap(map)
            Button(top, map, mod, (0, (no + 2 / 6)), cover_size, 1075, 42)

top.mainloop()
