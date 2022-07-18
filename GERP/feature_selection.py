#!/usr/bin/env python


# Author : @cb46


import argparse
from pathlib import Path
from collections import defaultdict



parser = argparse.ArgumentParser(description = 'Obtain unique non-overlapping instances of each feature type')
parser.add_argument('--gff', help = 'Annotation in GFF (General Feature Format) format [e.g. abrostola_tripartita_gca905340225v1.gff3]')
parser.add_argument('--feature', help = 'Feature type [default: CDS]', type = str, default = "CDS")
parser.add_argument('--o', help = 'Output directory')



def parse_annotation(gff_f, feature):
	mygff = defaultdict(list)
	with open(gff_f) as f:
		for line in f:
			if not line.startswith('#'):
				contig, ensembl, feature_type, start, end, dot, strand, value, info = line.strip().split()
				start, end = int(start), int(end)
				if feature_type == "gene":
					gene_id, gene_biotype, gene_id, gene_version = info.split(';')
					gene = gene_id.split('=')[1]
					gene_contig, gene_start, gene_end, gene_strand = contig, start, end, strand
					mygff[gene_contig, "gene", gene_start, gene_end, gene_strand, gene]
				elif feature_type == feature:
					feature_start, feature_end = start, end
					mygff[gene_contig, "gene", gene_start, gene_end, gene_strand, gene].append([feature_start, feature_end])
	return mygff



def unique_nonoverlapping_instances(mygff, feature, refGenome, path):
	for gene in mygff:
		intervals = mygff[gene]
		if intervals:
			# Sort genomic coordinates
			intervals.sort(key=lambda interval: interval[0])
			merged = [intervals[0]]
			# Combine overlapping features
			for current in intervals:
				previous = merged[-1]
				if current[0] <= previous[1]:
					previous[1] = max(previous[1], current[1])
				else:
					merged.append(current)
				output_file = Path(path, refGenome + '.' + gene[0] + '.merged.bed')
				with open(output_file, 'a') as out:
					for genomic_coordinate in merged:
						chromosome = refGenome + '.' + gene[0]
						out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(chromosome, "Ensembl", feature, genomic_coordinate[0], genomic_coordinate[1], '.', gene[4], '.', gene[5]))




if __name__ == "__main__":
	args = parser.parse_args()
	# Obtain name of genome from the annotation file (e.g. abrostola_tripartita_gca905340225v1.gff3)
	refGenome = Path(args.gff).stem
	# Create output directory if it doesn't exist
	path = Path(args.o)
	path.mkdir(parents=True, exist_ok=True)
	# Obtain unique non-overlapping instances
	select_features = parse_annotation(args.gff, args.feature)
	unique_elements = unique_nonoverlapping_instances(select_features, args.feature, refGenome, path)

  