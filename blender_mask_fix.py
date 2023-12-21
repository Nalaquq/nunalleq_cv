import os
import cv2 as cv
import numpy as np
import PIL.Image

path="blender_masks/"

os.chdir(path)
for x in os.listdir():
    image=PIL.Image.open(x)
    rgba=image.convert("RGBA")
    datas=rgba.getdata()
    newData=[]
    for item in datas:
        if item[0]!=255 and item[1]!=255 and item[2]!=255:
            newData.append((0,0,0,1))
        else: 
            newData.append(item)
    rgba.putdata(newData)
    rgba.save(x, "PNG")
    print(image)
    #image=image.save(x)

