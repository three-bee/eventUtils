#!/bin/bash
 
declare -a datasets=("ambush_2" "ambush_4" "ambush_6" "bamboo_2" "cave_4" "market_2" "market_5" "market_6" "mountain_1" "temple_2" )
declare -a ctlist=("5" "15" "25" )

for seq in "${datasets[@]}"; do
    for ct in "${ctlist[@]}"; do
        cd /home/bbatu/258_"$ct"_RESULTS/SPN/"$seq"/
        ffmpeg -framerate 50 -i maskedflow%03d.png -vb 50M video.mpg
        mv /home/bbatu/258_"$ct"_RESULTS/SPN/"$seq"/video.mpg /home/bbatu/Desktop/maskedvideo/"$seq"_masked_"$ct".mpg
    done
done