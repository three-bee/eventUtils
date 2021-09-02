""" 
Converts a ROS bag file containing DAVIS events into hdf5 format.
Data in the hdf5 file has the same organization as in MVSEC dataset: https://daniilidis-group.github.io/mvsec/

This script does not transfer image_raw data from bag to hdf5.

This scripts reads the bag file, converts event data into csv format, creates two text files containing event timestamps &
raw frame timestamps, then transfers the data inside these three files into hdf5.
Resulting hdf5 file will contain: 
-events (x,y,timestamp,polarity)
-image_raw_event_inds (closest corresponding event number at the instance of image)
-image_raw_ts (image timestamps)

Extracted .txt files can be later utilized by flow2hdf5.py.

One important thing to note is that runtime performance of this script is far from ideal. 

Bahri Batuhan Bilecen, 2021 August
"""

import os
import argparse
from progress.bar import Bar
import h5py
import pandas as pd
import rosbag
from bagpy import bagreader
import numpy as np
import math

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return int(idx-1)
    else:
        return int(idx)

parser = argparse.ArgumentParser()
parser.add_argument('--bagfile', type=str, help='.bag file')
parser.add_argument('--eventtopic', type=str, default='dvs', help='Topic name in which the event data are stored. Mostly it is dvs(ETH Zurich Event Dataset), davis(MVSEC), or cam0 (ESIM output)')
args = parser.parse_args()

#TODO: Generalize below path
#TODO: Automatize eventtopic argument
#tempfile = self.datafolder + "/" + topic.replace("/", "-") + ".csv"
csv_path = os.path.splitext(args.bagfile)[0] + '/' + args.eventtopic + '-events.csv'
hdf5_out = os.path.splitext(args.bagfile)[0] + '.hdf5'

#TODO: Migrate completely to either bagpy or rosbag later
if not os.path.isfile(csv_path):
    #Using bagpy for reading events
    print('.csv file is not present. Converting the events in .bag to .csv first.')
    input_bag = bagreader(args.bagfile)
    events_csv = input_bag.message_by_topic('/' + args.eventtopic + '/events')
    print('Transfered event data inside .bag to .csv.')
    #Using rosbag for reading images
    input_bag = rosbag.Bag(args.bagfile, "r")
else:
    print('.csv file is present. Not reading .bag file.')
    #Using rosbag for reading images
    input_bag = rosbag.Bag(args.bagfile, "r")


with h5py.File(hdf5_out,"w") as outfile:
    event_stamps_file = open(os.path.splitext(args.bagfile)[0]+'/event_stamps.txt', 'a')
    all_events = pd.read_csv(csv_path)['events']
    print('Converted .bag to .csv.')

    #Calculating total number of messages
    total_events = sum([len(i.split(',')) for i in all_events])
    total_images = input_bag.get_message_count(topic_filters=('/' + args.eventtopic + '/image_raw'))
    print('total_events: %d'%total_events)
    print('total_images: %d'%total_images)

    #Initializing datasets (compatible with MVSEC dataset hdf5 format)
    group_left = outfile.create_group("davis").create_group("left")
    hdf_events = group_left.create_dataset("events", (total_events,4))
    hdf_image_raw_event_inds = group_left.create_dataset("image_raw_event_inds",(total_images,1),compression="gzip")
    hdf_image_raw_ts = group_left.create_dataset("image_raw_ts",(total_images,1),compression="gzip")
        
    #Writing events
    #TODO: Do everything with read_messages func of rosbag
    bar_events = Bar('Writing events...', max=total_events)
    event_count = 0

    for event_group in all_events:
        event_group_splitted = event_group.split(',')
        for event in event_group_splitted:
            #Format of hdf5 dataset: hdf_events[:,:] = [x,y,(secs and nsecs),polarity]
            #Format of .bag file for each event = [x,y,t,secs,nsecs,polarity]
            event_splitted = event.split('\n')

            #x and y
            hdf_events[event_count,0] = int(''.join(i for i in event_splitted[0] if i.isnumeric()))
            hdf_events[event_count,1] = int(''.join(i for i in event_splitted[1] if i.isnumeric()))
            
            #t: secs, nsecs
            secs = int(''.join(i for i in event_splitted[3] if i.isnumeric()))
            nsecs = float(''.join(i for i in event_splitted[4] if i.isnumeric()))
            event_timestamp = secs*10e8 + nsecs
            #TODO: Clear txt first before appending
            event_stamps_file.write(str(event_timestamp)+'\n') #Store all nsec data for later comparison
            hdf_events[event_count,2] = event_timestamp
            
            #polarities
            if (event_splitted[5].find('True') == -1):
                hdf_events[event_count,3] = -1 #polarity (False)
            else:
                hdf_events[event_count,3] = 1 #polarity (True)
            
            bar_events.next()
            event_count += 1
    bar_events.finish()
    event_stamps_file.close()
    
    #Writing image timestamps
    bar_stamps = Bar('Writing timestamps...', max=total_images)
    image_count = 0

    event_stamps_file = open(os.path.splitext(args.bagfile)[0]+'/event_stamps.txt', 'r')
    event_timestamp_arr = [float(i) for i in event_stamps_file.readlines()]
    event_stamps_file.close()

    image_stamps_file = open(os.path.splitext(args.bagfile)[0]+'/image_stamps.txt', 'w')
    
    for topic, image_msgs, t in input_bag.read_messages(topics=[('/' + args.eventtopic + '/image_raw')]):
        hdf_image_raw_event_inds[image_count,0] = find_nearest(event_timestamp_arr, t.to_nsec())
        
        hdf_image_raw_ts[image_count,0] = t.to_nsec()
        image_stamps_file.write(str(t.to_nsec())+'\n')

        bar_stamps.next()
        image_count += 1
    bar_stamps.finish()
    
    image_stamps_file.close()

input_bag.close()

