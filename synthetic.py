import cv2
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt


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
def obj_list():
    # could fix this solution with try/except blocks
    PATH_MAIN = args.src
    try:
        obj_dict = {}
        folder_count = len(next(os.walk(PATH_MAIN))[1])
        for f in range(folder_count):
            obj_dict[f] = {
                "folder": next(os.walk(PATH_MAIN))[1][f],
                "longest_min": 150,
                "longest_max": 800,
            }
        # delete the "baclkground images" since it does not have the same directory structure
        del obj_dict[1]
        print(obj_dict)
    except:
        print(f"didn't work is {PATH_MAIN} a directory?")
        pass

    try:
        for k, _ in obj_dict.items():
            folder_name = obj_dict[k]["folder"]
            files_imgs = sorted(
                os.listdir(os.path.join(PATH_MAIN, folder_name, "images"))
            )
            files_imgs = [
                os.path.join(PATH_MAIN, folder_name, "images", f) for f in files_imgs
            ]
            files_masks = sorted(
                os.listdir(os.path.join(PATH_MAIN, folder_name, "masks"))
            )
            files_masks = [
                os.path.join(PATH_MAIN, folder_name, "masks", f) for f in files_masks
            ]
            obj_dict[k]["images"] = files_imgs
            obj_dict[k]["masks"] = files_masks
            print(
                f"\nThe first five files from directory the sorted list of images in {folder_name}:",
                obj_dict[k]["images"][:5],
            )
            print(
                f"\nThe first five files from the sorted list of masks in {folder_name}:",
                obj_dict[k]["masks"][:5],
            )

        files_bg_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, "background")))
        files_bg_imgs = [
            os.path.join(PATH_MAIN, "background", f) for f in files_bg_imgs
        ]
        print(
            "\nThe first five files from the sorted list of background images:",
            files_bg_imgs[:5],
        )
    except:
        print(
            "An error occurred. Ensure that your files are ordered and sorted into images and masks correctly."
        )
        pass
    return obj_dict


if args.src:
    obj_list()
else:
    print(
        "no source directory given. Please use python3 synthetic.py -h to learn more."
    )


def get_img_and_mask(img_path, mask_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mask = cv2.imread(mask_path)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    mask_b = mask[:, :, 0] == 0  # This is boolean mask
    mask = mask_b.astype(np.uint8)  # This is binary mask

    return img, mask


###NEED TO FIX


def test_mask():
    x = obj_list()
    print("\n \n \n Testing Binary Mask Conversion \n \n \n")
    img_path = x[0]["images"][0]
    mask_path = x[0]["masks"][0]
    img, mask = get_img_and_mask(img_path, mask_path)
    print("Image file:", img_path)
    print("Mask file:", mask_path)
    print("\nShape of the image of the object:", img.shape)
    print("Shape of the binary mask:", mask.shape)
    fig, ax = plt.subplots(1, 2, figsize=(16, 7))
    ax[0].imshow(img)
    ax[0].set_title("Object", fontsize=18)
    ax[1].imshow(mask)
    ax[1].set_title("Binary mask", fontsize=18)
    print("\n \n \n Binary Mask Conversion is Sucessful \n \n \n")


test_mask()


def resize_img(img, desired_max, desired_min=None):
    h, w = img.shape[0], img.shape[1]

    longest, shortest = max(h, w), min(h, w)
    longest_new = desired_max
    if desired_min:
        shortest_new = desired_min
    else:
        shortest_new = int(shortest * (longest_new / longest))

    if h > w:
        h_new, w_new = longest_new, shortest_new
    else:
        h_new, w_new = shortest_new, longest_new

    transform_resize = A.Compose(
        [
            A.Sequential(
                [A.Resize(h_new, w_new, interpolation=1, always_apply=False, p=1)], p=1
            )
        ]
    )

    transformed = transform_resize(image=img)
    img_r = transformed["image"]

    return img_r
