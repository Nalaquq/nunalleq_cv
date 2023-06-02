import cv2 as cv
import os

def obj_list():
    PATH_MAIN='data'
    try: 
        obj_dict ={}
        folder_count=len(next(os.walk(PATH_MAIN))[1])
        for f in range(folder_count):
            obj_dict[f]={'folder': next(os.walk(PATH_MAIN))[1][f],'longest_min': 150, 'longest_max': 800}
    except: 
        print(f"didn't work is {PATH_MAIN} a directory?")
        pass
    print(obj_dict)

obj_list()
