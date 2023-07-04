import cv2
import os
from zipfile import ZipFile

def rename():
    os.chdir('noise/hand/mask_hand')
    subdirectory = input("Enter name of subdirectory:")
    cwd = os.getcwd()
    os.chdir(f'./{subdirectory}')
    imgList = os.listdir()
    
    for x in imgList:
        img = cv2.imread(x)
        os.chdir(cwd)
        imgName = os.path.splitext(x)
        imgNum = int(imgName[0])
        if imgNum < 10:
            newImgName = 'hand70' + str(imgNum)
        else:
            newImgName = 'hand7' + str(imgNum)
        print(newImgName)
        cv2.imwrite(f'{newImgName}.jpg', img)
        os.chdir(f'./{subdirectory}')
    
rename()