import cv2
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import albumentations as A
import time
from tqdm import tqdm
from datetime import datetime
import yaml

parser = argparse.ArgumentParser(description="Generates Synthetic Datasets for YOLO Object Detection.")
# add optional arguments
parser.add_argument(
    "-src",
    "-src_dir",
    type=os.path.abspath,
    help="the source directory containing your data for generation",
)
parser.add_argument(
    "-n",
    "-num",
    type=int,
    help="The number of images to be generated. Images will be generated according to a 80/20/20 Train/Test/Val split",
    default=1000
)
parser.add_argument("-min", type=int, help="the minimum size of images produced. The default is 150px.", default=150)
# this will throw an error is a max size is selected that is larger than the background image size. Fix this. 
parser.add_argument("-max", type=int, help="The maximum size of generated images. The defauly is 800px. An error will occur if a max size is selected that is larger than the background image size.", default=800)
parser.add_argument("-erase", "-erase_existing_dataset", type=bool, help="Boolean value that deletes all files in dataset directory before generation. Default is false, so that labels and images will not be deleted between runs.", default=True)
parser.add_argument("-config", "-config_file", type=os.path.abspath, help="The location of the config.yaml file containing your albumentations configurations. If not selected synthetic.py will try to load config.py", default='config.yaml')
args = parser.parse_args()

if args.src:
    PATH_MAIN = args.src
else:
    PATH_MAIN = os.path.abspath('data')
    print(
        f"\n No source directory given. Main Path set to {PATH_MAIN}. Please use python3 synthetic.py -h to learn more.\n"
    )
if args.config:
    yaml_path = args.config
else: 
    yaml_path = 'config.yaml'

def obj_list():
    """
    Generates a dictionary that maps folder indices to their respective image and mask file paths.

    This function walks through directories located at the path specified by PATH_MAIN, constructing a
    dictionary where each entry corresponds to a folder and contains details like the folder name, and
    paths to all image and mask files within that folder. The function also adjusts for a specific folder
    (typically at index 1) by removing it from the dictionary, assuming it does not follow the same
    directory structure as the others.

    The function assumes the global variables `args.min` and `args.max` are accessible and contain
    relevant bounds which are included in the dictionary for each folder. It also relies on a global
    PATH_MAIN which should be defined externally and points to the main directory path.

    Returns:
        dict: A dictionary where each key is an integer index and each value is a dictionary containing
        the 'folder' name, a list of 'images' file paths, a list of 'masks' file paths, and the
        'longest_min' and 'longest_max' values pulled from global args.

    Raises:
        FileNotFoundError: If PATH_MAIN does not exist or specified folders are not found.
        IndexError: If there is an attempt to delete a non-existing index from the dictionary.

    Note:
        This function directly modifies the dictionary by deleting the entry at index 1 and assumes
        specific global configurations, which might lead to errors if not properly setup.
    """
    obj_dict = {}
    folder_count = len(next(os.walk(PATH_MAIN))[1])
    for f in range(folder_count):
        obj_dict[f] = {
            "folder": next(os.walk(PATH_MAIN))[1][f],
            "longest_min": args.min,
            "longest_max": args.max,
            }
    # delete the "background images" since it does not have the same directory structure
    del obj_dict[1]
    temp_list=list(range(len(obj_dict)))
    obj_dict=dict(zip(temp_list, list(obj_dict.values())))
    for k, _ in obj_dict.items():
        folder_name = obj_dict[k]["folder"]

        files_imgs = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, "images")))
        files_imgs = [os.path.join(PATH_MAIN, folder_name, "images", f) for f in files_imgs]

        files_masks = sorted(os.listdir(os.path.join(PATH_MAIN, folder_name, "masks")))
        files_masks = [os.path.join(PATH_MAIN, folder_name, "masks", f) for f in files_masks]
        obj_dict[k]["images"] = files_imgs
        obj_dict[k]["masks"] = files_masks
    return obj_dict


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


def get_img_and_mask(img_path: str, mask_path: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load an image and its corresponding mask from specified file paths, convert both to RGB format, and process the mask into a binary format.

    Parameters:
        img_path (str): The file path to the image.
        mask_path (str): The file path to the mask image.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing the RGB image and the binary mask as NumPy arrays.

    Raises:
        IOError: If the files specified do not exist or cannot be opened.
        ValueError: If the image files are not in a format that can be converted to RGB.

    Example:
        >>> image, binary_mask = get_img_and_mask("path/to/image.jpg", "path/to/mask.jpg")
        This will load the image and mask from the specified paths, convert them to RGB, and convert the mask to a binary format.
    """
    img = cv2.imread(img_path)
    if img is None:
        raise IOError(f"Unable to open image file: {img_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mask = cv2.imread(mask_path)
    if mask is None:
        raise IOError(f"Unable to open mask file: {mask_path}")
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    mask_b = mask[:, :, 0] == 0  # This is a boolean mask indicating where the mask is applied
    mask = mask_b.astype(np.uint8)  # Convert boolean mask to binary format

    return img, mask


def resize_img(img: np.ndarray, desired_max: int, desired_min: int =None) -> np.ndarray:
    """
    Resize an image to the specified maximum and optional minimum dimensions, maintaining aspect ratio.

    Parameters:
        img (np.ndarray): The input image as a NumPy array.
        desired_max (_int_): The maximum size for the longest dimension of the image.
        desired_min (Optional[_int_]): The minimum size for the shortest dimension of the image.
            If None, the aspect ratio is maintained.

    Returns:
        np.ndarray: The resized image as a NumPy array.

    Raises:
        ValueError: If any of the input dimensions are not positive integers.

    Example:
        >>> img_resized = resize_img(image_array, 800, 600)
        This would resize `image_array` to have the longest dimension be 800 pixels, and the
        shortest dimension proportionally resized to maintain aspect ratio, unless 600 is provided,
        then it resizes the shortest dimension to 600 pixels directly.
    """
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


def load_transformations_from_yaml(yaml_path: str) -> list:
    """
    Load transformation configurations from a YAML file and create corresponding Albumentations objects.

    Parameters:
        yaml_path (str): Path to the YAML file containing the transformation configurations.

    Returns:
        dict: A dictionary containing Albumentations Compose objects for background and object transformations.
    """
    # Load YAML file
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)

    # Helper function to construct an Albumentations Compose object from a list of transformations
    def construct_transformation(transform_config):
        transformations = []
        for transform in transform_config:
            for key, value in transform.items():
                transform_class = getattr(A, key)
                transformations.append(transform_class(**value))
        return A.Compose(transformations)

    # Create transformation objects from YAML config
    transformations = {key: construct_transformation(value) for key, value in config.items()}
    print("Background and Object Transformations loaded successfully.")
    return transformations 

transformation_objects = load_transformations_from_yaml(yaml_path)
transforms_bg_obj = transformation_objects['transforms_bg_obj']
transforms_obj = transformation_objects['transforms_obj']




def resize_transform_obj(img: np.ndarray, mask: np.ndarray, longest_min: int, longest_max: int, transforms: bool = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Resizes an image and its corresponding mask to a new size, randomly determined within specified bounds for the longest dimension, and optionally applies additional transformations.

    Parameters:
        img (np.ndarray): The image to be transformed, expected to be a NumPy array.
        mask (np.ndarray): The mask corresponding to the image, expected to be a NumPy array of the same dimensions as the image.
        longest_min (int): The minimum value for the longest dimension of the resized image and mask.
        longest_max (int): The maximum value for the longest dimension of the resized image and mask.
        transforms (bool): A function or composed set of transformations to apply to the resized image and mask. If False, no additional transformations are applied.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing the resized and possibly transformed image and mask.

    Raises:
        ValueError: If the `longest_min` is greater than `longest_max`.
        IndexError: If the dimensions of `mask` do not match the dimensions of `img`.

    Example:
        >>> image, mask = resize_transform_obj(image_array, mask_array, 300, 500)
        This will resize `image_array` and `mask_array` to a random size between 300 and 500 pixels for the longest dimension,
        maintaining the aspect ratio, and apply additional transformations if provided.
    """
    h, w = mask.shape[:2]

    longest, shortest = max(h, w), min(h, w)
    longest_new = np.random.randint(longest_min, longest_max)
    shortest_new = int(shortest * (longest_new / longest))

    if h > w:
        h_new, w_new = longest_new, shortest_new
    else:
        h_new, w_new = shortest_new, longest_new

    transform_resize = A.Resize(h_new, w_new, interpolation=1, always_apply=False, p=1)

    transformed_resized = transform_resize(image=img, mask=mask)
    img_t = transformed_resized["image"]
    mask_t = transformed_resized["mask"]

    if transforms:
        transformed = transforms(image=img_t, mask=mask_t)
        img_t = transformed["image"]
        mask_t = transformed["mask"]

    return img_t, mask_t

def add_obj(img_comp, mask_comp, img, mask, x, y, idx):
    """
    img_comp - composition of objects
    mask_comp - composition of objects` masks
    img - image of object
    mask - binary mask of object
    x, y - coordinates where center of img is placed
    Function returns img_comp in CV2 RGB format + mask_comp
    """
    h_comp, w_comp = img_comp.shape[0], img_comp.shape[1]

    h, w = img.shape[0], img.shape[1]

    x = x - int(w / 2)
    y = y - int(h / 2)

    mask_b = mask == 1
    mask_rgb_b = np.stack([mask_b, mask_b, mask_b], axis=2)

    if x >= 0 and y >= 0:
        h_part = h - max(
            0, y + h - h_comp
        )  # h_part - part of the image which gets into the frame of img_comp along y-axis
        w_part = w - max(
            0, x + w - w_comp
        )  # w_part - part of the image which gets into the frame of img_comp along x-axis

        img_comp[y : y + h_part, x : x + w_part, :] = (
            img_comp[y : y + h_part, x : x + w_part, :]
            * ~mask_rgb_b[0:h_part, 0:w_part, :]
            + (img * mask_rgb_b)[0:h_part, 0:w_part, :]
        )
        mask_comp[y : y + h_part, x : x + w_part] = (
            mask_comp[y : y + h_part, x : x + w_part] * ~mask_b[0:h_part, 0:w_part]
            + (idx * mask_b)[0:h_part, 0:w_part]
        )
        mask_added = mask[0:h_part, 0:w_part]

    elif x < 0 and y < 0:
        h_part = h + y
        w_part = w + x

        img_comp[0 : 0 + h_part, 0 : 0 + w_part, :] = (
            img_comp[0 : 0 + h_part, 0 : 0 + w_part, :]
            * ~mask_rgb_b[h - h_part : h, w - w_part : w, :]
            + (img * mask_rgb_b)[h - h_part : h, w - w_part : w, :]
        )
        mask_comp[0 : 0 + h_part, 0 : 0 + w_part] = (
            mask_comp[0 : 0 + h_part, 0 : 0 + w_part]
            * ~mask_b[h - h_part : h, w - w_part : w]
            + (idx * mask_b)[h - h_part : h, w - w_part : w]
        )
        mask_added = mask[h - h_part : h, w - w_part : w]

    elif x < 0 and y >= 0:
        h_part = h - max(0, y + h - h_comp)
        w_part = w + x

        img_comp[y : y + h_part, 0 : 0 + w_part, :] = (
            img_comp[y : y + h_part, 0 : 0 + w_part, :]
            * ~mask_rgb_b[0:h_part, w - w_part : w, :]
            + (img * mask_rgb_b)[0:h_part, w - w_part : w, :]
        )
        mask_comp[y : y + h_part, 0 : 0 + w_part] = (
            mask_comp[y : y + h_part, 0 : 0 + w_part]
            * ~mask_b[0:h_part, w - w_part : w]
            + (idx * mask_b)[0:h_part, w - w_part : w]
        )
        mask_added = mask[0:h_part, w - w_part : w]

    elif x >= 0 and y < 0:
        h_part = h + y
        w_part = w - max(0, x + w - w_comp)

        img_comp[0 : 0 + h_part, x : x + w_part, :] = (
            img_comp[0 : 0 + h_part, x : x + w_part, :]
            * ~mask_rgb_b[h - h_part : h, 0:w_part, :]
            + (img * mask_rgb_b)[h - h_part : h, 0:w_part, :]
        )
        mask_comp[0 : 0 + h_part, x : x + w_part] = (
            mask_comp[0 : 0 + h_part, x : x + w_part]
            * ~mask_b[h - h_part : h, 0:w_part]
            + (idx * mask_b)[h - h_part : h, 0:w_part]
        )
        mask_added = mask[h - h_part : h, 0:w_part]

    return img_comp, mask_comp, mask_added


def create_bg_with_noise(
    files_bg_imgs,
    files_bg_noise_imgs,
    files_bg_noise_masks,
    bg_max=1920,
    bg_min=1080,
    max_objs_to_add=60,
    longest_bg_noise_max=1000,
    longest_bg_noise_min=200,
    blank_bg=False,
):
    if blank_bg:
        img_comp_bg = np.ones((bg_min, bg_max, 3), dtype=np.uint8) * 255
        mask_comp_bg = np.zeros((bg_min, bg_max), dtype=np.uint8)
    else:
        idx = np.random.randint(len(files_bg_imgs))
        img_bg = cv2.imread(files_bg_imgs[idx])
        img_bg = cv2.cvtColor(img_bg, cv2.COLOR_BGR2RGB)
        img_comp_bg = resize_img(img_bg, bg_max, bg_min)
        mask_comp_bg = np.zeros(
            (img_comp_bg.shape[0], img_comp_bg.shape[1]), dtype=np.uint8
        )

    for i in range(1, np.random.randint(max_objs_to_add) + 2):
        idx = np.random.randint(len(files_bg_noise_imgs))
        img, mask = get_img_and_mask(
            files_bg_noise_imgs[idx], files_bg_noise_masks[idx]
        )
        x, y = np.random.randint(img_comp_bg.shape[1]), np.random.randint(
            img_comp_bg.shape[0]
        )
        img_t, mask_t = resize_transform_obj(
            img,
            mask,
            longest_bg_noise_min,
            longest_bg_noise_max,
            transforms=transforms_bg_obj,
        )
        img_comp_bg, _, _ = add_obj(img_comp_bg, mask_comp_bg, img_t, mask_t, x, y, i)

    return img_comp_bg


def check_areas(mask_comp, obj_areas, overlap_degree=0.3):
    obj_ids = np.unique(mask_comp).astype(np.uint8)[1:-1]
    masks = mask_comp == obj_ids[:, None, None]

    ok = True

    if len(np.unique(mask_comp)) != np.max(mask_comp) + 1:
        ok = False
        return ok

    for idx, mask in enumerate(masks):
        if np.count_nonzero(mask) / obj_areas[idx] < 1 - overlap_degree:
            ok = False
            break

    return ok


def create_composition(
    img_comp_bg, max_objs=15, overlap_degree=0.2, max_attempts_per_obj=10
):
    obj_dict=obj_list()
    img_comp = img_comp_bg.copy()
    h, w = img_comp.shape[0], img_comp.shape[1]
    mask_comp = np.zeros((h, w), dtype=np.uint8)

    obj_areas = []
    labels_comp = []
    num_objs = np.random.randint(max_objs) + 2

    i = 1

    for _ in range(1, num_objs):
        obj_idx = np.random.randint(len(obj_dict)) #+ 1

        for _ in range(max_attempts_per_obj):
            imgs_number = len(obj_dict[obj_idx]["images"])
            idx = np.random.randint(imgs_number)
            img_path = obj_dict[obj_idx]["images"][idx]
            mask_path = obj_dict[obj_idx]["masks"][idx]
            img, mask = get_img_and_mask(img_path, mask_path)

            x, y = np.random.randint(w), np.random.randint(h)
            longest_min = obj_dict[obj_idx]["longest_min"]
            longest_max = obj_dict[obj_idx]["longest_max"]
            img, mask = resize_transform_obj(
                img, mask, longest_min, longest_max, transforms=transforms_obj
            )

            if i == 1:
                img_comp, mask_comp, mask_added = add_obj(
                    img_comp, mask_comp, img, mask, x, y, i
                )
                obj_areas.append(np.count_nonzero(mask_added))
                labels_comp.append(obj_idx)
                i += 1
                break
            else:
                img_comp_prev, mask_comp_prev = img_comp.copy(), mask_comp.copy()
                img_comp, mask_comp, mask_added = add_obj(
                    img_comp, mask_comp, img, mask, x, y, i
                )
                ok = check_areas(mask_comp, obj_areas, overlap_degree)
                if ok:
                    obj_areas.append(np.count_nonzero(mask_added))
                    labels_comp.append(obj_idx)
                    i += 1
                    break
                else:
                    img_comp, mask_comp = img_comp_prev.copy(), mask_comp_prev.copy()

    return img_comp, mask_comp, labels_comp, obj_areas


def create_yolo_annotations(mask_comp, labels_comp):
    comp_w, comp_h = mask_comp.shape[1], mask_comp.shape[0]

    obj_ids = np.unique(mask_comp).astype(np.uint8)[1:]
    masks = mask_comp == obj_ids[:, None, None]

    annotations_yolo = []
    for i in range(len(labels_comp)):
        pos = np.where(masks[i])
        xmin = np.min(pos[1])
        xmax = np.max(pos[1])
        ymin = np.min(pos[0])
        ymax = np.max(pos[0])

        xc = (xmin + xmax) / 2
        yc = (ymin + ymax) / 2
        w = xmax - xmin
        h = ymax - ymin

        annotations_yolo.append(
            [
                labels_comp[i] - 1,
                round(xc / comp_w, 5),
                round(yc / comp_h, 5),
                round(w / comp_w, 5),
                round(h / comp_h, 5),
            ]
        )

    return annotations_yolo


def generate_dataset(imgs_number, folder, split="train"):
    time_start = time.time()
    timing=datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    for j in tqdm(range(imgs_number)):
        img_comp_bg = create_bg_with_noise(
            files_bg_imgs, files_bg_noise_imgs, files_bg_noise_masks, max_objs_to_add=60
        )

        img_comp, mask_comp, labels_comp, _ = create_composition(
            img_comp_bg, max_objs=15, overlap_degree=0.2, max_attempts_per_obj=10
        )

        img_comp = cv2.cvtColor(img_comp, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(folder, split, "images/{}"+timing+".jpg").format(j), img_comp)

        annotations_yolo = create_yolo_annotations(mask_comp, labels_comp)
        for i in range(len(annotations_yolo)):
            with open(os.path.join(folder, split, "labels/{}"+timing+".txt").format(j), "a") as f:
                f.write(" ".join(str(el) for el in annotations_yolo[i]) + "\n")
    time_end = time.time()
    time_total = round(time_end - time_start)
    time_per_img = round((time_end - time_start) / imgs_number, 1)

    print(
        "Generation of {} synthetic images is completed. It took {} seconds, or {} seconds per image".format(
            imgs_number, time_total, time_per_img
        )
    )
    print("Images are stored in '{}'".format(os.path.join(folder, split, "images")))
    print(
        "Annotations are stored in '{}'".format(os.path.join(folder, split, "labels"))
    )

def mkdir():
    try:
        print("\n\n Checking Project Paths:")
        home = os.path.abspath(os.getcwd())
        try:
            os.mkdir(dataset)
            os.chdir(dataset)
        except:
            os.chdir(dataset)
        dir_list = ["train", "test", "val"]
        sub_dir_list = ["images", "labels"]
        for x in dir_list:
            os.mkdir(x)
        print("\n\t Home Directory: '{}' ".format(home))
        print("\n\t Data For Generation: '{}'".format(PATH_MAIN))
    except:
        dataset = os.path.join(home, "dataset")
        print("\n\t Home Directory:'{}' ".format(home))
        print("\n\t Data For Generation: '{}' ".format(PATH_MAIN))
        print("\n\t Generated Datasets Stored in: '{}' ".format(dataset))
        #insert if statement for argparse libary that runs clean remove existing dataset -del if set to true. Default will be false..   
        total_number=[]
        if args.erase==True: 
            print("\n\tThe Erase function has been enabled \n")
            print("\n Removing Old Datasets from: {}".format(dataset))
            for root, dirs, files in os.walk(dataset):
                for name in tqdm(files): 
                    total_number.append(files)
                    if name.endswith(".jpg"):
                        selected_files=os.path.join(root, name)
                        os.remove(selected_files)
                    if name.endswith('.txt'):
                        selected_files=os.path.join(root,name)
                        os.remove(selected_files)
            print("\n{} files were deleted.".format(len(total_number)))
        else: 
            for root, dirs, files in os.walk(dataset):
                for name in (files):
                    if name.endswith(".jpg"):
                        selected_files=os.path.join(root, name)
                    if name.endswith('.txt'):
                        selected_files=os.path.join(root,name)
            print("\n\t {} files were deleted.".format(len(total_number)))
            print("\n\t There are {} labels and images in this dataset.".format(len(selected_files)))
            print("\n Beginning Data Generation\n")
            pass                                  

#to use with generate to create CLI for first input in generate_dataset  
def test_train_val_split():
    if args.n <=10:
        print("At least 10 images are needed for an 80/10/10 dataset. Using the default value of 1000 training images.")
        training_set=800
        test_set=100
        validation_set=100
    else: 
        total_dataset=args.n
        test_set=int((.10*total_dataset)//1)
        validation_set=int((.10*total_dataset)//1)
        training_set=int((.80*total_dataset)//1)
        print(f"\n {total_dataset} images and labels will be split into a 80/10/10 training/test/validation set containing: \n {training_set} training images \n {test_set} test images \n {validation_set} validation images.")
    print(test_set)
    return test_set, training_set, validation_set


def generate():
    obj_list()
    mkdir()
    ttv=test_train_val_split()
    generate_dataset(ttv[0], folder="dataset", split="test")
    generate_dataset(ttv[2], folder="dataset", split="val")
    generate_dataset(ttv[1], folder="dataset", split="train")


generate()

