# Visualization Implementation Plan

## Overview
Write a python script to visualize the MAGport summary results in an interactive HTML report like multiQC. The report should include:
- A summary table (SUMMARY_TSV), enabling sorting and filtering.
- Visualizations for key metrics:
  - Genome size distribution (bar chart)
  - GC content distribution (histogram)
  - Completeness vs. Contamination (scatter plot)
  - Traits: Completeness, Contamination, GC, num_16S, (radargram)
  - MIMAG quality distribution (pie chart)
  - GTDB Taxonomic classification at different ranks (bar chart for each rank, with the most frequent taxa at left)

- Interactive elements:
  - Tooltips for detailed info on hover
  - Clickable rows in the summary table to highlight corresponding points in visualizations
- Export options for visualizations (PNG, SVG)
- Responsive design for various screen sizes
- Modular code structure for easy updates and additions
- Elegant and user-friendly UI/UX design

## Input table format sample
```tsv
MAG	num_contigs	genome_size_bp	N50	GC	sum_ambiguous_bases	num_ORFs	Completeness	Contamination	GUNC_status	Park_Score	MIMAG_level	num_tRNAs	num_16S_rRNAs	num_23S_rRNAs	num_5S_rRNAs	16S_NCBI_taxonomy	16S_blastn_identity	GTDB_taxonomy
GCF_024346955.1_vmangrovi	2	5007139	3674542	45.62	0	4345	100	0	TRUE	99.9	HQ	95	8	8	9	Vibrio mangrovi strain MSSRF38 16S ribosomal RNA, partial sequence	99.928	d__Bacteria;p__Pseudomonadota;c__Gammaproteobacteria;o__Enterobacterales;f__Vibrionaceae;g__Vibrio;s__Vibrio mangrovi
MAG1	28	903669	68826	38.27	0	1029	93.95	0	TRUE	92.55	MQ	45	1	1	0	Methanobacterium kanagiense strain 169 16S ribosomal RNA, partial sequence	77.045	d__Archaea;p__Aenigmatarchaeota;c__Aenigmatarchaeia;o__Aenigmatarchaeales;f__Aenigmatarchaeaceae;g__;s__
MAG209	240	1863239	10236	45.01	0	2002	91.26	1.88	TRUE	69.86	MQ	35	1	0	0	Infirmifilum uzonense strain 1807-2 16S ribosomal RNA, complete sequence	79.051	d__Archaea;p__Thermoproteota;c__Bathyarchaeia;o__Bathyarchaeales;f__Bathycorpusculaceae;g__A05DMB-2;s__
```
