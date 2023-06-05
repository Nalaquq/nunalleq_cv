import cv2 as cv
import os
import argparse


parser = argparse.ArgumentParser()
#add optional arguments
parser.add_argument("-src", "-src_directory", type=os.path.abspath, help="the source directory containing your training dataset")
args=parser.parse_args()

def obj_list():
    #include optional positional argument
    PATH_MAIN=args.src
    try: 
        obj_dict ={}
        folder_count=len(next(os.walk(PATH_MAIN))[1])
        for f in range(folder_count):
            obj_dict[f]={'folder': next(os.walk(PATH_MAIN))[1][f],'longest_min': 150, 'longest_max': 800}
        #delete the "baclkground images" since it does not have the same directory structure
        del obj_dict[0]
    except: 
        print(f"didn't work is {PATH_MAIN} a directory?")
        pass
    print(obj_dict)

    try:
        for k, _ in obj_dict.items():
            folder_name = obj_dict[k]['folder']
            files_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, 'images')))
            files_imgs = [os.path.join(PATH_MAIN, folder_name, 'images', f) for f in files_imgs]
            files_masks = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, 'masks')))
            files_masks = [os.path.join(PATH_MAIN, folder_name, 'masks', f) for f in files_masks]
            obj_dict[k]['images'] = files_imgs
            obj_dict[k]['masks'] = files_masks
            print(f"\nThe first five files from directory the sorted list of images in {folder_name}:", obj_dict[k]['images'][:5])
            print(f"\nThe first five files from the sorted list of masks in {folder_name}:", obj_dict[k]['masks'][:5]) 
            
        files_bg_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, 'background')))
        files_bg_imgs = [os.path.join(PATH_MAIN, 'background', f) for f in files_bg_imgs]
        print("\nThe first five files from the sorted list of background images:", files_bg_imgs[:5])
    except:
        print("An error occurred. Ensure that your files are ordered and sorted into images and masks correctly.")
        pass






if args.src:
    obj_list()
else:
    print("no source directory given. Please use python3 synthetic.py -h to learn more.")



