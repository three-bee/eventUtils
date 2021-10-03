'''
Saves accumulated events (count_data files, outputs of Spike-FlowNet: https://github.com/chan8972/Spike-FlowNet) as binary images.
'''

import numpy as np
import cv2
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--countdatapath', type=str, help='Path of count_data folder')
args = parser.parse_args()

countdata_path_list = sorted(next(os.walk(args.countdatapath))[2]) #Does not include subfolders. All items in the directory must be npy files.
#Keep in mind that countdata_path_list is NOT in order, even after the sorting function.

dst = args.countdatapath + '/spikeimages'
try:
    os.makedirs(dst)
except OSError:
    pass

for data in countdata_path_list:
    count_data = np.load(args.countdatapath + '/' + data)
    spike_img = np.zeros((count_data.shape[1],count_data.shape[2]))

    for i in range(0,count_data.shape[3]):
        spike_img += count_data[0,:,:,i]
        spike_img += count_data[1,:,:,i]

    ret, spike_img = cv2.threshold(spike_img, 0, 255, cv2.THRESH_BINARY)
    
    filename = '%05d.png'%int(data[:-4]) #For sorting purposes
    cv2.imwrite(dst + '/' + filename, spike_img)