#!/usr/bin/env python


# Author: @cb46


import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt



parser = argparse.ArgumentParser(description = 'Plot mutation events in cactus alignment')
parser.add_argument('--count', help = 'Summary table of mutation events in cactus alignemt')
parser.add_argument('--species_list', help = 'Tab delimited species list file')
parser.add_argument('--o', help = 'Output directory')



def get_species_name_genome(species_list):
        genomes = {}
        with open(species_list) as f:
                for line in f:
                        assembly, tol_id, p_class, species_name, superfamily = line.strip().split()
                        genome = species_name.lower() + "_" + assembly.replace('GCA_', 'gca').replace('.', 'v')
                        genomes[genome] = species_name
        return genomes



def summary_mutation_events_alignment(count_f, genomes, path):
        mymut = {}
        with open(count_f) as f:
                next(f)
                next(f)
                for line in f:
                        line = line.strip().split()
                        if line:
                                # Skip ancestors
                                if 'Anc' not in line[0] and 'Total' not in line[0] and 'Average' not in line[0]:
                                        genomeName = line[0].replace(',', '')
                                        species_name = genomes[genomeName]
                                        mut = [int(i.replace(',', '')) for i in line[5:]]
                                        substitutions, transitions, transversions, insertions, deletions, inversions, duplications, transpositions, other = mut[0], mut[1], mut[2], mut[8], mut[10], mut[12], mut[14], mut[16], mut[18]
                                        mymut[species_name] = [substitutions, transitions, transversions, insertions, deletions, inversions, duplications, transpositions]
        
        df = pd.DataFrame.from_dict(mymut, orient="index", columns = ['Substitutions', 'Transitions', 'Transversions', 'Insertions', 'Deletions', 'Inversions', 'Duplications', 'Transpositions'])
        log_df = df.apply(lambda x: np.log10(x) if np.issubdtype(x.dtype, np.number) else x)
        plt.rcParams.update({'font.size': 4})
        fig = plt.figure(figsize=(10, 3))
        figure = Path(path, 'summary_mutations_in_alignment.pdf')
        log_df.plot.bar(stacked = True)
        plt.ylabel('Log10 count of mutation events in cactus alignment')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig(figure, dpi = 500, bbox_inches = 'tight')



if __name__ == "__main__":
        args = parser.parse_args()
        # Create output directory if it doesn't exist
        p = Path(args.o)
        p.mkdir(parents=True, exist_ok=True)
        # Plot mutation events in cactus alignment
        species_name = get_species_name_genome(args.species_list)
        summary_mutations = summary_mutation_events_alignment(args.count, species_name, args.o)


