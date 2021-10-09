#!/bin/sh
ctresh=25
resolution=258
crop=True
resizeratio=3.379844

utilspath=/home/bbatu/eventUtils
event_dataset=/home/bbatu/SINTELOUT_"$resolution"_"$ctresh"
flow_dataset=/home/bbatu/SINTEL/flow_1008fps
results=/home/bbatu/"$resolution"_"$ctresh"_RESULTS

cd "$event_dataset"
for folder in */; do
    data=${folder%/}
    printf "Processing: (%s)\n" "$data"
    python "$utilspath"/metrics.py \
    --gtflowpath="$flow_dataset"/"$data"_lowrate/ \
    --predflowpath="$results"/FN2/"$data".epoch-0-flow-field/ \
    --ratio="$resizeratio" \
    --crop="$crop" \
    --maskpath="$event_dataset"/"$data"/count_data/spikeimages/ \
    --maskenabled=True
done