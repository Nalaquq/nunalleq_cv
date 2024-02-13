import subprocess
import cv2
import numpy as np 
import os

def nvidia_check():
    try: 
        subprocess.check_output("nvidia-smi")
        print(subprocess.check_output(['nvidia-smi']).decode())
        #x=subprocess.check_output("nvcc --version")
        #print(x)
        print("Nvidia GPU detected!")
        return True
    except Exception: 
        print("No Nvidia GPU detected")
        return False 

def cuda_enable():
    test=nvidia_check()
    if test==True: 
        print("Enabling CUDA Support")
        import cupy as np
    if test==False: 
        print("No Cuda support detected. \n Image Processing Pipeline will be run on CPU")
        import numpy as np

def img_erode(path):
    filepath=path
    img = cv2.imread(path)
    assert img is not None, "file could not be read, check with os.path.exists()"
    #kernel = np.ones((5,5),np.uint8)
    #erosion = cv2.erode(img,kernel,iterations = 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    erode = cv2.erode(img, kernel, iterations=2)
    cv2.imwrite(path, erode)

def img_dialate(path):
    filepath=path
    img=cv2.imread(path)
    assert img is not None, "file could not be read, check with os.path.exists()"
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    dilate=cv2.dilate(img, kernel, iterations=2)
    cv2.imwrite(path, dilate)

def dir_comp(path):
    home=os.getcwd()
    os.chdir(path)
    files=os.listdir()
    print(files)
    return files


if __name__=="__main__":
    #mask_erode()
    files=dir_comp("data/ulus/images")
    for file in files: 
        img_erode(file)
        print(file)

