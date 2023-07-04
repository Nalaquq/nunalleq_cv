import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import argparse

def objList():
    pathMain = 'noise'
    objDict = {}
    folderCount = len(next(os.walk(pathMain))[1])
    for f in range(folderCount):
        objDict[f] = {
            'folder': next(os.walk(pathMain))[1][f],
            'longestMin': 150,
            'longestMax': 800,
        }
    print(objDict)

    for k, _ in objDict.items():
        folderName = objDict[k]['folder']

        if folderName == 'background':
            filesBgImgs = sorted(os.listdir(os.path.join(pathMain, 'background')))
            filesBgImgs = [os.path.join(pathMain, 'background', f) for f in filesBgImgs]

            print(
                '\nThe first five files from the sorted list of background images:',
                filesBgImgs[:5],
            )
        elif folderName == 'bg_noise':
            filesBgNoiseImgs = sorted(os.listdir(os.path.join(pathMain, folderName, 'images')))
            filesBgNoiseImgs = [os.path.join(pathMain, folderName, 'images', f) for f in filesImgs]
        
            filesBgNoiseMasks = sorted(os.listdir(os.path.join(pathMain, folderName, 'masks')))
            filesBgNoiseMasks = [os.path.join(pathMain, folderName, 'masks', f) for f in filesMasks]
            
            print(
                f'\nThe first five files from the sorted list of images in {folderName}:',
                filesBgNoiseImgs[:5],
            )
            print(
                f'\nThe first five files from the sorted list of masks in {folderName}:',
                filesBgNoiseMasks[:5],
            )
        else:
            filesImgs = sorted(os.listdir(os.path.join(pathMain, folderName, 'images')))
            filesImgs = [os.path.join(pathMain, folderName, 'images', f) for f in filesImgs]
        
            filesMasks = sorted(os.listdir(os.path.join(pathMain, folderName, 'masks')))
            filesMasks = [os.path.join(pathMain, folderName, 'masks', f) for f in filesMasks]
        
            objDict[k]['images'] = filesImgs
            objDict[k]['masks'] = filesMasks
            
            print(
                f'\nThe first five files from the sorted list of images in {folderName}:',
                objDict[k]['images'][:5],
            )
            print(
                f'\nThe first five files from the sorted list of masks in {folderName}:',
                objDict[k]['masks'][:5],
            )

def mkdir():
    print('\nChecking Project Paths:')
    home = os.path.abspath(os.getcwd())
    dirList = ['train', 'test', 'val']
    subDirList = ['images', 'labels']

    if os.path.isdir(os.path.join(home, 'dataset')) == False:
        os.mkdir('dataset')
        print('\nFolder "dataset" was created.')
    dataset = os.path.join(home, 'dataset')
    os.chdir(dataset)  

    for k, datasetFolder in enumerate(dirList):
        if os.path.isdir(os.path.join(dataset, dirList[k])) == False:
            os.mkdir(datasetFolder)
            print(f'\nFolder "{datasetFolder}" was created.')
        
        subDir = os.path.join(dataset, datasetFolder)
        os.chdir(subDir)

        for l, subFolder in enumerate(subDirList):
            if os.path.isdir(os.path.join(subDir, subDirList[l])) == False:
                os.mkdir(subFolder)
                print(f'\nFolder "{subFolder}" was created.')
        os.chdir(dataset)
    print('\nAll folders necessary for synthetic dataset generation have been made or confirmed.')
    
    totalNumber = []
    for root, dirs, files in os.walk(dataset):
        for name in files:
            totalNumber.append(files)
            if name.endswith('.JPG'):
                selectedFiles = os.path.join(root, name)
                os.remove(selectedFiles)
            if name.endswith('.txt'):
                selectedFiles = os.path.join(root, name)
                os.remove(selectedFiles)
    print(f'\n{len(totalNumber)} file(s) were deleted.\n')

mkdir()





'''parser = argparse.ArgumentParser(description='Creates Image Masks and Generates Synthetic Datasets for YOLO Object Detection.')

parser.add_argument(
    
)'''