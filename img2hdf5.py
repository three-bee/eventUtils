"""
Writes grayscale image data from a directory into an existing hdf5 file.
Data in the hdf5 file has the same organization as in MVSEC dataset: https://daniilidis-group.github.io/mvsec/

Bahri Batuhan Bilecen, 2021 August
"""

import os
import sys
import argparse
import h5py
from progress.bar import Bar
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('--imagepath', type=str, help='Path of image files')
parser.add_argument('--hdf5path', type=str, help='Path of hdf5 file')
args = parser.parse_args()

with h5py.File(args.hdf5path,"w") as outfile:
    image_path_list = sorted(next(os.walk(args.imagepath))[2])
    total_images = len(image_path_list)
    x = cv2.imread(args.imagepath + image_path_list[0]).shape[0]
    y = cv2.imread(args.imagepath + image_path_list[0]).shape[1]

    hdf_image_raw = outfile.create_group("davis").create_group("left").create_dataset("image_raw", (total_images,x,y), compression="gzip")
    
    #Writing images
    bar_image_raw = Bar('Writing grayscale images...', max=total_images)
    image_count = 0

    for image in image_path_list:
        grayscale = cv2.imread(args.imagepath + image, 0)
        hdf_image_raw[image_count] = grayscale
        bar_image_raw.next()
        image_count += 1

    bar_image_raw.finish()