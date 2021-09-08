#!/bin/sh
data=ambush_2
rate=4
resizeratio=4
c_pos=0.15
c_neg=0.15
exposure_time_ms=10.0
crop=True

#Preprocessing of images
python preprocess.py --imgpath=/home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/ --flowpath=/home/bbatu/TEST/flow_1008fps/"$data"/ --rate="$rate" --resizeratio="$resizeratio"
ffmpeg -r 200 -i /home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/resized/cropped/cropped%3d.png -vb 50M /home/bbatu/TEST/"$data".mpg

#Creating events from images
source ~/setupeventsim.sh
roscd esim_ros 
python scripts/generate_stamps_file.py -i /home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/resized/cropped/ -r 200.0
rosrun esim_ros esim_node \
 --data_source=2 \
 --path_to_output_bag=/home/bbatu/TEST/"$data".bag \
 --path_to_data_folder=/home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/resized/cropped/ \
 --ros_publisher_frame_rate=60 \
 --exposure_time_ms="$exposure_time_ms" \
 --use_log_image=1 \
 --log_eps=0.1 \
 --contrast_threshold_pos="$c_pos" \
 --contrast_threshold_neg="$c_neg"
rm /home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/resized/cropped/images.csv
cd /home/bbatu/eventUtils/

#Converting bag data to hdf5
python bag2hdf5.py --bagfile=/home/bbatu/TEST/"$data".bag --eventtopic='cam0'
python2 bag2img.py --bagfile=/home/bbatu/TEST/"$data".bag --eventtopic='cam0'
python img2hdf5.py --imagepath=/home/bbatu/TEST/"$data"/frames/ --hdf5path=/home/bbatu/TEST/"$data".hdf5
python flow2hdf5.py --hdf5path=/home/bbatu/TEST/"$data".hdf5 \
 --gtflowpath=/home/bbatu/TEST/flow_1008fps/"$data"/ \
 --lowratepath=/home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"_lowrate/resized/cropped/ \
 --highratepath=/home/bbatu/TEST/sintel_data_1008fps/clean_1008fps/"$data"/resized/cropped/ \
 --crop="$crop"

#SpikeFlowNet split coding
python /home/bbatu/Spike-FlowNet/encoding/split_coding.py --save-dir=/home/bbatu/TEST/ --save-env=/home/bbatu/TEST/"$data"/ --data-path=/home/bbatu/TEST/"$data".hdf5

#Moving & renaming
mv /home/bbatu/TEST/"$data".bag /home/bbatu/TEST/"$data"/
mv /home/bbatu/TEST/"$data".hdf5 /home/bbatu/TEST/"$data"/"$data"_data.hdf5
mv /home/bbatu/TEST/"$data".mpg /home/bbatu/TEST/"$data"/
mv /home/bbatu/TEST/"$data"_gt.hdf5 /home/bbatu/TEST/"$data"/