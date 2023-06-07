import cv2
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import albumentations as A
import time
from tqdm import tqdm


parser = argparse.ArgumentParser()
# add optional arguments
parser.add_argument(
    "-src",
    "-source_directory",
    type=os.path.abspath,
    help="the source directory containing your training dataset",
)
args = parser.parse_args()


# need to fix with try/except loop. Include obj_dict[1] background
if args.src:
    PATH_MAIN = args.src
else:
    print(
        "no source directory given. Please use python3 synthetic.py -h to learn more."
    )


obj_dict = {
    1: {"folder": "caveg", "longest_min": 150, "longest_max": 800},
    2: {"folder": "endblades", "longest_min": 150, "longest_max": 800},
    3: {"folder": "tops", "longest_min": 150, "longest_max": 800},
    4: {"folder": "ulus", "longest_min": 150, "longest_max": 800},
}

for k, _ in obj_dict.items():
    folder_name = obj_dict[k]["folder"]

    files_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, "images")))
    files_imgs = [os.path.join(PATH_MAIN, folder_name, "images", f) for f in files_imgs]

    files_masks = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, "masks")))
    files_masks = [
        os.path.join(PATH_MAIN, folder_name, "masks", f) for f in files_masks
    ]

    obj_dict[k]["images"] = files_imgs
    obj_dict[k]["masks"] = files_masks
    print(f"\nThe first five files from directory the sorted list of images in {folder_name}:",
                obj_dict[k]["images"][:5],
            )
    print(f"\nThe first five files from the sorted list of masks in {folder_name}:",
                obj_dict[k]["masks"][:5],
            )
print(
    "The first five files from the sorted list of battery images:",
    obj_dict[1]["images"][:5],
)
print(
    "\nThe first five files from the sorted list of battery masks:",
    obj_dict[1]["masks"][:5],
)

files_bg_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, "background")))
files_bg_imgs = [os.path.join(PATH_MAIN, "background", f) for f in files_bg_imgs]

files_bg_noise_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, "bg_noise", "images")))
files_bg_noise_imgs = [
    os.path.join(PATH_MAIN, "bg_noise", "images", f) for f in files_bg_noise_imgs
]
files_bg_noise_masks = sorted(os.listdir(os.path.join(PATH_MAIN, "bg_noise", "masks")))
files_bg_noise_masks = [
    os.path.join(PATH_MAIN, "bg_noise", "masks", f) for f in files_bg_noise_masks
]

print(
    "\nThe first five files from the sorted list of background images:",
    files_bg_imgs[:5],
)
print(
    "\nThe first five files from the sorted list of background noise images:",
    files_bg_noise_imgs[:5],
)
print(
    "\nThe first five files from the sorted list of background noise masks:",
    files_bg_noise_masks[:5],
)

