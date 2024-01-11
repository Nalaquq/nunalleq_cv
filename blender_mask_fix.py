import os
import cv2 as cv
import numpy as np
import PIL.Image
import shutil

def image_mover():
    path="blender_masks/"
    source = '/home/nalkuq/nunalleq_cv/data/ulus/'
    destination_images = '/home/nalkuq/nunalleq_cv/data/ulus/masks/'
    destination_masks = "/home/nalkuq/nunalleq_cv/data/ulus/masks"

    os.chdir(source)
    #for x in os.listdir():
    #if x.endswith(".glb"):
        #generate(x)
    for x in os.listdir():
        if x.endswith("mask.png"):
            print(x)
            src_path = os.path.join(source, x)
            dst_path = os.path.join(destination_masks, x)
            shutil.move(src_path, dst_path)
            os.chdir(source)
        if x.endswith("image.png"): 
            print(x)
            src_path = os.path.join(source, x)
            dst_path = os.path.join(destination_images, x)
            shutil.move(src_path, dst_path)
            os.chdir(source)

def mask_fix():
    os.chdir(destination_masks)
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
        #image=image.save(x)i

def mask_delete(path):
    os.chdir(path)
    for x in os.listdir():
        if x.endswith("mask.png"):
            print(x)
            os.remove(x)




os.chdir("data/ulus/masks")
for x in os.listdir():
    filename=x
    img = cv.imread(x, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    kernel = np.ones((5,5),np.uint8)
    opening = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
    cv.imwrite(filename, opening)
    print(x)

  
