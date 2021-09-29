"""
Extracts image_raw data from a bag file (containing event data).
Run with Python 2 as imgmsg_to_cv2 function does not work with Python 3.

Extracted image files can be later utilized by flow2hdf5.py.

Bahri Batuhan Bilecen, 2021 August
"""

import os
import argparse
import rosbag
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

parser = argparse.ArgumentParser()
parser.add_argument('--bagfile', type=str, help='.bag file')
parser.add_argument('--eventtopic', type=str, default='dvs', help='Topic name in which the event data are stored. Mostly it is dvs(http://rpg.ifi.uzh.ch/davis_data.html), davis(MVSEC), or cam0 (ESIM output)')
args = parser.parse_args()

input_bag = rosbag.Bag(args.bagfile, "r")
bridge = CvBridge()

total_images = input_bag.get_message_count(topic_filters=('/' + args.eventtopic + '/image_raw'))

save_path = os.path.splitext(args.bagfile)[0] + '/frames'
try:
    os.makedirs(save_path)
except OSError:
    pass

count = 0
for topic, msg, t in input_bag.read_messages(topics=[('/' + args.eventtopic + '/image_raw')]):
    cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")
    cv2.imwrite(save_path + "/frame%06i.png" % count, cv_img)
    count += 1
input_bag.close()

print('Done. See:' + save_path)
