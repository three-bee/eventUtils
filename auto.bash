#!/bin/sh
#Paths
outfolder=/home/bbatu/SINTELOUT
imgfolder=/home/bbatu/SINTEL/sintel_data_1008fps/clean_1008fps
flowfolder=/home/bbatu/SINTEL/flow_1008fps
spikeflownetpath=/home/bbatu/Spike-FlowNet
utilspath=/home/bbatu/eventUtils

#Preprocessing params
crop=True
rate=4
resizeratio=4

#ESIM Params
eventtopic=cam0
c_pos=0.15
c_neg=0.15
exposure_time_ms=10.0

cd "$imgfolder"
for folder in */; do
    data=${folder%/}
    printf "############## 1. Preprocessing images: (%s)\n" "$data"
    python "$utilspath"/preprocess.py --imgpath="$imgfolder"/"$data"/ --flowpath="$flowfolder"/"$data"/ --rate="$rate" --resizeratio="$resizeratio"
    ffmpeg -r 200 -i "$imgfolder"/"$data"/resized/cropped/cropped%3d.png -vb 50M "$outfolder"/"$data".mpg

    #ssim alias
    printf "############## 2. Creating events from images: (%s)\n" "$data"
    source ~/setupeventsim.sh
    roscd esim_ros 
    python scripts/generate_stamps_file.py -i "$imgfolder"/"$data"/resized/cropped/ -r 200.0
    rosrun esim_ros esim_node \
    --data_source=2 \
    --path_to_output_bag="$outfolder"/"$data".bag \
    --path_to_data_folder="$imgfolder"/"$data"/resized/cropped/ \
    --ros_publisher_frame_rate=60 \
    --exposure_time_ms="$exposure_time_ms" \
    --use_log_image=1 \
    --log_eps=0.1 \
    --contrast_threshold_pos="$c_pos" \
    --contrast_threshold_neg="$c_neg"
    rm "$imgfolder"/"$data"/resized/cropped/images.csv

    printf "############## 3. Bagfile to hdf5: (%s)\n" "$data"
    python "$utilspath"/bag2hdf5.py --bagfile="$outfolder"/"$data".bag --eventtopic="$eventtopic"
    python2 "$utilspath"/bag2img.py --bagfile="$outfolder"/"$data".bag --eventtopic="$eventtopic"
    python "$utilspath"/img2hdf5.py --imagepath="$outfolder"/"$data"/frames/ --hdf5path="$outfolder"/"$data".hdf5
    python "$utilspath"/flow2hdf5.py --hdf5path="$outfolder"/"$data".hdf5 \
    --gtflowpath="$flowfolder"/"$data"/ \
    --lowratepath="$imgfolder"/"$data"_lowrate/resized/cropped/ \
    --highratepath="$imgfolder"/"$data"/resized/cropped/ \
    --crop="$crop"

    printf "############## 4. Split encoding: (%s)\n" "$data"
    python "$spikeflownetpath"/encoding/split_coding.py --save-dir="$outfolder"/ --save-env="$outfolder"/"$data"/ --data-path="$outfolder"/"$data".hdf5

    printf "############## 5. Cleanup and renaming: (%s)\n" "$data"
    mv "$outfolder"/"$data".bag "$outfolder"/"$data"/
    mv "$outfolder"/"$data".hdf5 "$outfolder"/"$data"/"$data"_data.hdf5
    mv "$outfolder"/"$data".mpg "$outfolder"/"$data"/
    mv "$outfolder"/"$data"_gt.hdf5 "$outfolder"/"$data"/
done