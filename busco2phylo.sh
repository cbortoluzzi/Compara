#!/bin/bash


# Author: @cb46


# Export path
export PATH=/software/team118/mafft-7.475-with-extensions/bin:$PATH
export PATH=/lustre/scratch123/tol/teams/durbin/users/cb46/softwares/trimal/source:$PATH
export PATH=/lustre/scratch123/tol/teams/durbin/users/cb46/softwares/standard-RAxML-master:$PATH



if [ -z $1 ]; then
        echo "Usage: ./busco2phylo.sh <list.fish> <directory.busco.output>"
fi



FISH=$1
DIR=$2
DATE="$(date +'%Y%m%d')"
BUSCO="busco_"$DATE


mkdir -p $BUSCO


echo "./busco2phylo.sh $FISH $DIR"


# Count number of genomes
num_genomes=`cat $FISH | wc -l`


# Unique complete BUSCO genes
cat $FISH | while read species; do cat $DIR/$species/vertebrata_odb10_metaeuk/run_vertebrata_odb10/full_table.tsv | grep -v '^#' | awk '$2=="Complete" {print $1}' >> $BUSCO/complete_busco_ids.txt;done
sort $BUSCO/complete_busco_ids.txt | uniq -c | awk '$1=="'$num_genomes'"{print $2}' > $BUSCO/final_busco_ids.txt

mkdir -p $BUSCO/alignment
mkdir -p $BUSCO/trimAl


cat $BUSCO/final_busco_ids.txt | while read busco_id;
do
	mkdir -p $BUSCO/fasta/$busco_id
	cat $FISH | while read species
	do
		for faa in $DIR/$species/vertebrata_odb10_metaeuk/run_vertebrata_odb10/busco_sequences/single_copy_busco_sequences/${busco_id}.faa;
		do
		# Reformat amino-acid fasta sequence of each single copy gene and species
		cat $faa | awk '/^>/{print ">'$species'"; next}{print}' > $BUSCO/fasta/$busco_id/$species\_${busco_id}.fa
		done
	done

	cat $BUSCO/fasta/$busco_id/*_$busco_id.fa >> $BUSCO/alignment/$busco_id.aln
	# Perform alignment with mafft
	echo "mafft --amino $BUSCO/alignment/$busco_id.aln > $BUSCO/alignment/$busco_id.aln.mafft"
	mafft --amino $BUSCO/alignment/$busco_id.aln > $BUSCO/alignment/$busco_id.aln.mafft
	rm $BUSCO/alignment/$busco_id.aln

	# Trim alignment with trimal
	echo "trimal -in $BUSCO/alignment/$busco_id.aln.mafft -out $BUSCO/trimAl/$busco_id.aln.mafft.trimal -gt 0.8 -st 0.001 -resoverlap 0.75 -seqoverlap 80"
	trimal -in $BUSCO/alignment/$busco_id.aln.mafft -out $BUSCO/trimAl/$busco_id.aln.mafft.trimal -gt 0.8 -st 0.001 -resoverlap 0.75 -seqoverlap 80
done


# Generate supermatrix
python3 ../../../codes/superalignment.py $BUSCO/trimAl


# Run Raxml
echo "raxmlHPC-PTHREADS-SSE3 -T 8 -f a -m PROTGAMMAJTT -N 100 -n my_busco_phylo -s $BUSCO/trimAl/supermatrix.aln.faa -p 13432 -x 89090"
raxmlHPC-PTHREADS-SSE3 -T 8 -f a -m PROTGAMMAJTT -N 100 -n my_busco_phylo -s $BUSCO/trimAl/supermatrix.aln.faa -p 13432 -x 89090
