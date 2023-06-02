import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import os


# how you could automate tihs process withkey words
def get_it_done():
    print(os.getcwd())
    os.chdir("images")
    print(os.getcwd())
    img_list = os.listdir()
    print(img_list)
    for x in img_list:
        jpg = ".jpg"
        if x.endswith(jpg):
            img = cv.imread(x)
            # flip from BGR to RGB
            corrected_img = np.flip(img, axis=-1)
            # print(img.shape)
            # plt.imshow(corrected_img)
            # plt.show()
        else:
            print(x, "is not an JPG")


def Canny():
    get_it_done()
    img = cv.imread("fish.jpg", cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    edges = cv.Canny(img, 100, 200)
    plt.subplot(121), plt.imshow(img, cmap="gray")
    plt.title("Original Image"), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(edges, cmap="gray")
    plt.title("Edge Image"), plt.xticks([]), plt.yticks([])
    plt.show()


def harris():
    filename = "fish.jpg"
    img = cv.imread(filename)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv.cornerHarris(gray, 2, 3, 0.04)
    # result is dilated for marking the corners, not important
    dst = cv.dilate(dst, None)
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst > 0.01 * dst.max()] = [0, 0, 255]
    cv.imshow("dst", img)
    if cv.waitKey(0) & 0xFF == 27:
        cv.destroyAllWindows()


def good():
    get_it_done()
    img = cv.imread("fish.jpg")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    corners = cv.goodFeaturesToTrack(gray, 25, 0.01, 10)
    corners = np.int0(corners)
    for i in corners:
        x, y = i.ravel()
        cv.circle(img, (x, y), 3, 255, -1)
    plt.imshow(img), plt.show()


def sift():
    get_it_done()
    img = cv.imread("fish.jpg")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    sift = cv.SIFT_create()
    kp = sift.detect(gray, None)
    cv.imwrite("sift_keypoints.jpg", img)
    plt.imshow(img), plt.show()


good()
