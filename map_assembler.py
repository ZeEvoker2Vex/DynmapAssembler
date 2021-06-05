import os
# import glob
import sys

from PIL import Image
from timeit import default_timer as timer

# One problem is that the program will generate too big a map because the dynmap will
# have generated a part of the map that is far from the rest, and that you are not interested in.
# You will have to crop the png to keep what you are interested in.
# So be patient, it should not take more than 5 minutes.
# 40960x22400 takes 3m40s for me

start_time = timer()

# Put in the map folder the content of "dynmap/web/tiles/world/flat" folder.
path = "map\\"

if not os.path.exists(path):
    _ = input("Process finished, 'map' folder doesn't exist !\nPress any key to exit.")
    sys.exit()

files = []
x_min = 0
y_min = 0
x_max = 0
y_max = 0
# for file in glob.glob(path + "*.jpg"):
print("Listing all files...")
for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        # Do not add file containing "z" because that is a zoom out tile
        if "z" not in file and file != "":
            # Get the file name and its coordinates
            file_name = os.path.basename(file[:file.rindex(".")])
            file_coordinates = file_name.split("_")
            x_file = int(file_coordinates[0])
            y_file = int(file_coordinates[1])

            # Update min & max
            if x_min > x_file:
                x_min = x_file
            elif y_min > y_file:
                y_min = y_file
            elif x_max < x_file:
                x_max = x_file
            elif y_max < y_file:
                y_max = y_file

            files.append([os.path.join(dirpath, file), file_coordinates])

if not files:
    _ = input("Process finished, 'map' folder is empty, but need the content of 'dynmap/web/tiles/world/flat' folder."
              "\nPress any key to exit.")
    sys.exit()

x_size = abs(x_max-x_min)
y_size = abs(y_max-y_min)

width = 128*x_size
height = 128*y_size

# print(files)
print("Min index (x,y) :", x_min, y_min)
print("Max index (x,y) :", x_max, y_max)
print("Space between (x,y) :", x_size, y_size)
# Image size = number of tiles in width and height x128 because a tile is 128x128
print("Image size (width,height) :", width, height)

map_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

# x of the file = the smaller it is the more to the left / y of the file = the smaller it is the more downwards
# ex Y : -25_-11 and -25_-12 : -12 will be on the left of -11
# ex X : -25_-11 and -26_-11 : -26 will be on the left of -25
print("Creating png (scale:", width, "x", height, ")")
for file in files:
    img = Image.open(file[0])
    img_width, img_height = img.size

    file_x = int(file[1][0])
    file_y = int(file[1][1])

    # More the file_x is small, more the tile is on the left
    img_x = abs(file_x - x_min) * 128
    # More the file_y is small, more the tile is at the bottom
    img_y = abs(y_max - file_y) * 128

    # Add the tile to the full map
    map_img.paste(img, (img_x, img_y))

map_img.save("map.png")

resize_width = width/4
resize_height = height/4

print("Resizing map to 1/1 scale (", resize_width, "x", resize_height, ")")
# 4x4 pixels = 1 block so resize the map to the 1:1 scale
map_img_resize = Image.new("RGBA", (width, height), (0, 0, 0, 0))
map_img_resize.paste(map_img, (0, 0, width, height))
map_img_resize.thumbnail((resize_width, resize_height), Image.ANTIALIAS)
map_img_resize.save("map-resize.png")

print("Creation of the PNG map completed in", timer()-start_time, "seconds.")
