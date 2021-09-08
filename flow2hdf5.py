"""
Creates a corresponding ground-truth optical flow .hdf5 file to the output of bag2hdf5.py.
Data in the hdf5 file has the same organization as in MVSEC dataset: https://daniilidis-group.github.io/mvsec/

This script matches the images created via img2hdf5.py (lower framerate) with higher framerate images,
both taken from the same video sequence, but with different sampling rates.
Each adjacent high framerate image pair must have a ground-truth optical flow .flo file.
Using the match as an index for image_stamps.txt file, corresponding flow files are first resized, then written to a .hdf5 file.

If images had to be cropped in 1:1 ratio from the middle, then flow files can be cropped accordingly as well with --crop flag.

Output of this script acts as a ground-truth optical flow counterpart to outputs of bag2hdf5 & img2hdf5.

Bahri Batuhan Bilecen, 2021 September
"""

import os
import argparse
import h5py
from progress.bar import Bar
import flowpy
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('--hdf5path', type=str, help='Path of the output of img2hdf5.py')
parser.add_argument('--gtflowpath', type=str, help='Path of ground truth .flo files')
parser.add_argument('--lowratepath', type=str, help='Path of image files extracted from hdf5 or rosbag file')
parser.add_argument('--highratepath', type=str, help='Path of high framerate image files')
parser.add_argument('--crop', type=bool, default=False, help='True if flow files in gtflowpath need to be cropped in 1:1 (from center).')
args = parser.parse_args()

highrate_path_list = sorted(next(os.walk(args.highratepath))[2]) #Does not include subfolders. All items in the directory must be images.
lowrate_path_list = sorted(next(os.walk(args.lowratepath))[2]) #Does not include subfolders. All items in the directory must be images.
gtflow_path_list = sorted(next(os.walk(args.gtflowpath))[2]) #Does not include subfolders. All items in the directory must be flo files.
image_stamps_path = os.path.splitext(args.hdf5path)[0] + '/image_stamps.txt'

gt_file = os.path.splitext(args.hdf5path)[0] + '_gt.hdf5'

y = cv2.imread(args.highratepath + highrate_path_list[0]).shape[0]
x = cv2.imread(args.highratepath + highrate_path_list[0]).shape[1]
crop_size = y if y<x else x

total_lowrate = len(lowrate_path_list)
total_highrate = len(highrate_path_list)
rate = round(total_highrate/total_lowrate)

print('Lowrate image number: %d'%total_lowrate)
print('Highrate image number: %d'%total_highrate)
print('Rate: %d'%rate)

bar_flow =  Bar('Writing flow files...', max=total_lowrate-1)

with h5py.File(gt_file,"w") as outfile, open(image_stamps_path,'r') as image_stamps:    
    group_left = outfile.create_group("davis").create_group("left")
    if args.crop:
        hdf_flow_dist = group_left.create_dataset("flow_dist", (total_lowrate-1,2,crop_size,crop_size), dtype='f8') 
    else:
        hdf_flow_dist = group_left.create_dataset("flow_dist", (total_lowrate-1,2,y,x), dtype='f8')
    hdf_flow_dist_ts = group_left.create_dataset("flow_dist_ts", (total_lowrate-1,), dtype='f8')

    stamps_list = image_stamps.readlines()
        
    for i in range(0,total_lowrate-1):
        flow = flowpy.flow_read(args.gtflowpath + gtflow_path_list[rate*i]) #0 rate rate*2 ...
        f_y,f_x,_ = flow.shape
        ratio = int(f_y/crop_size) if y<=x else int(f_x/crop_size)
        
        if args.crop:
            #First resize
            (x,y) = (int(f_x/ratio), int(f_y/ratio))
            u = cv2.resize(flow[...,0],(x,y))
            v = cv2.resize(flow[...,1],(x,y))
            #Then crop 1:1 image flow from the middle
            offset = int((x-crop_size)/2) if x>crop_size else int((y-crop_size)/2)
            u = u[..., offset : -offset]
            v = v[..., offset : -offset]
        else:
            u = cv2.resize(flow[...,0],(x,y))
            v = cv2.resize(flow[...,1],(x,y))

        hdf_flow_dist[i,0] = u
        hdf_flow_dist[i,1] = v

        hdf_flow_dist_ts[i] = float(stamps_list[i])
        bar_flow.next()
bar_flow.finish()
