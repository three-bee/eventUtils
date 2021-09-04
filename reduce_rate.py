"""
Samples images according to a given rate.
"""
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--highratepath', type=str, help='Path of high framerate images')
parser.add_argument('--rate', type=int, help='Rate of downsampling')
args = parser.parse_args()

highrate_path_list = sorted(next(os.walk(args.highratepath))[2]) #Does not include subfolders. All items in the directory must be images.

dst = args.highratepath + 'lowrate'
try:
    os.makedirs(dst)
except OSError:
    pass

total_highrate = len(highrate_path_list)
for i in range(0,total_highrate):
    try:
        src = args.highratepath + highrate_path_list[i*args.rate]
    except IndexError:
        break
    command = 'cp ' + src + ' ' + dst
    os.popen(command)
