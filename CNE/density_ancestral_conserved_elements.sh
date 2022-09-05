#!/bin/bash


# Author : @cb46


# Export path
export PATH=/lustre/scratch123/tol/teams/durbin/users/cb46/softwares:$PATH


if [ -z $1 ]; then
	echo "Usage: ./density.sh <ancestral conserved elements> <genome file size>"
	exit -1
fi


ancestral_f=$1
genome=$2


mkdir -p ancestral_conserved_elements_density

species_name=$(basename $ancestral_f .bed)

# Calculate density in N bp window: we are using a window size of 100 kb, but this number can be changed
bedtools makewindows -g $genome -w 100000 > ancestral_conserved_elements_density/$species_name.window.bed
# We will consider only ancestral conserved elements that do not contain repeats
cat $ancestral_f | awk 'OFS="\t"{if($7 == 0.0)print $1,$2,$2+$3}' | bedtools coverage -a ancestral_conserved_elements_density/$species_name.window.bed -b stdin > ancestral_conserved_elements_density/$species_name.100kb.bed
rm ancestral_conserved_elements_density/$species_name.window.bed

# Average density in N bp window
cat ancestral_conserved_elements_density/$species_name.100kb.bed | awk '{sum+=$4}END{print sum/NR}'
