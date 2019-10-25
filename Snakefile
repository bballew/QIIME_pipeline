#! /usr/bin/env python3

"""CGR QIIME2 pipeline for microbiome analysis.

AUTHORS:
    S. Sevilla Chill
    W. Zhou
    B. Ballew

This pipeline uses the QIIME2 suite to classify sequence data,
calculate relative abundance, and (eventually) perform alpha- and beta-
diversity analysis.

INPUT:
    - Manifest file
        - First X columns are required as shown here:
            #SampleID       External-ID     Sample-Type     Source-Material
            Source-PCR-Plate        Run-ID  Project-ID      Reciept Sample_Cat
            SubjectID       Sample_Aliquot  Ext_Company     Ext_Kit Ext_Robot
            Homo_Method     Homo-Holder     Homo-Holder2    AFA Setting1
            AFA Setting2    Extraction Batch        Residual or Original
            Row     Column
    - config.yaml
    - (for production runs) run_pipeline.sh

TO RUN (choose one):

    A. Production run: Copy the run_pipeline.sh script to your
    directory and edit as needed, then execute that script.

    B. For dev/testing: Run the snakefile directly, e.g.:
        module load perl/5.18.0 miniconda/3  # miniconda3 has python 3.5.4
        source activate qiime2-2017.11  # or 2019.1
        conf=${PWD}/config.yml snakemake -s /path/to/pipeline/Snakefile
"""

import os
import re
import subprocess

# reference the config file
conf = os.environ.get("conf")
configfile: conf

# import variables from the config file
# TODO: write some error checking for the config file
meta_man_fullpath = config['metadata_manifest']
out_dir = config['out_dir'].rstrip('/') + '/'
exec_dir = config['exec_dir'].rstrip('/') + '/'
fastq_abs_path = config['fastq_abs_path'].rstrip('/') + '/'
qiime2_version = config['qiime2_version']
Q2_2017 = False
if qiime2_version == '2017.11':
    Q2_2017 = True
demux_param = config['demux_param']
input_type = config['input_type']
phred_score = config['phred_score']
filt_min = config['filt_param']
sampling_depth = config['sampling_depth']
max_depth = config['max_depth']
classify_method = config['classify_method']
REF_DB = config['reference_db']
denoise_method = config['denoise_method']
if denoise_method in ['dada2', 'DADA2']:
    trim_left_f = config['dada2_denoise']['trim_left_forward']
    trim_left_r = config['dada2_denoise']['trim_left_reverse']
    trunc_len_f = config['dada2_denoise']['truncate_length_forward']
    trunc_len_r = config['dada2_denoise']['truncate_length_reverse']


"""Parse manifest to set up sample IDs and other info

The manifest for CGR-generated data is largely automated via
LIMS.  External data will require a similarly-set up manifest
for this pipeline.

Samples must be associated with their run ID (aka flowcell) because
DADA2 requires analyses to occur on a per-flowcell basis.

Both run ID and project ID are required to generate the absolute
path to the fastq files (see get_orig_r*_fastq functions).

Note that run ID and project ID are currently being pulled from
the manifest based on column order.  If column order is subject to
change, we may want to pull based on column header.

TODO: change to name.  easier to check; possibly less subject to change.
"""
sampleDict = {}
RUN_IDS = []
with open(meta_man_fullpath) as f:
    next(f)
    for line in f:
        l = line.split('\t')
        if l[0] in sampleDict.keys():
            sys.exit('ERROR: Duplicate sample IDs detected in' + meta_man_fullpath)
        sampleDict[l[0]] = (l[5], l[6])  # SampleID, Run-ID, Project-ID
        RUN_IDS.append(l[5])
RUN_IDS = list(set(RUN_IDS))


def get_orig_r1_fq(wildcards):
    '''Return original R1 fastq with path based on filename

    Note there are some assumptions here (files always end with
    R1_001.fastq.gz; only one R1 fq per directory).  Same for
    following function.  This assumption should hold true even
    for historic projects, which had seq or extraction duplicates
    run in new folders.

    Note that assembling the absolute path to a fastq is a bit
    complex; however, this pattern is automatically generated
    and not expected to change in the forseeable future.
    '''
    (runID, projID) = sampleDict[wildcards.sample]
    p = fastq_abs_path + runID + '/CASAVA/L1/Project_' + projID + '/Sample_' + wildcards.sample + '/'
    file = [f for f in os.listdir(p) if f.endswith('R1_001.fastq.gz')]
    if len(file) != 1:
        sys.exit('ERROR: More than one R1 fastq detected in ' + p)
    return p + file[0]


def get_orig_r2_fq(wildcards):
    '''Return original R2 fastq with path based on filename
    See above function for more detail.
    '''
    (runID, projID) = sampleDict[wildcards.sample]
    p = fastq_abs_path + runID + '/CASAVA/L1/Project_' + projID + '/Sample_' + wildcards.sample + '/'
    file = [f for f in os.listdir(p) if f.endswith('R2_001.fastq.gz')]
    if len(file) != 1:
        sys.exit('ERROR: More than one R2 fastq detected in ' + p)
    return p + file[0]


refDict = {}
for i in REF_DB:
    refFile = os.path.basename(i)
    refNoExt = os.path.splitext(refFile)[0]
    refDict[refNoExt] = (i)


def get_ref_full_path(wildcards):
    '''
    '''
    (refFullPath) = refDict[wildcards.ref]
    return refFullPath


if denoise_method in ['dada2', 'DADA2'] and not Q2_2017:
    rule all:
        input:
            expand(out_dir + 'fastqs/' + '{sample}_R1.fastq.gz', sample=sampleDict.keys()),
            expand(out_dir + 'fastqs/' + '{sample}_R2.fastq.gz', sample=sampleDict.keys()),
            expand(out_dir + 'qzv_results/demux/{runID}_' + demux_param + '.qzv',runID=RUN_IDS),
            out_dir + 'qzv_results/table/final_filt_' + demux_param + '.qzv',
            out_dir + 'qzv_results/repseq/final_' + demux_param + '.qzv',
            out_dir + 'qza_results/core_metrics/rareifed_table.qza',
            out_dir + 'qzv_results/core_metrics/alpha_diversity_metadata.qzv',
            out_dir + 'qzv_results/core_metrics/rarefaction.qzv',
            expand(out_dir + 'qzv_results/taxonomy/' + classify_method + '_{ref}.qzv', ref=refDict.keys()),
            expand(out_dir + 'qzv_results/taxonomy/barplots_' + classify_method + '_{ref}.qzv', ref=refDict.keys()),
            expand(out_dir + 'qzv_results/dada2/stats/{runID}_' + demux_param + '.qzv', runID=RUN_IDS)  # has to be a more elegant way to do this.
else:
    rule all:
        input:
            expand(out_dir + 'fastqs/' + '{sample}_R1.fastq.gz', sample=sampleDict.keys()),
            expand(out_dir + 'fastqs/' + '{sample}_R2.fastq.gz', sample=sampleDict.keys()),
            expand(out_dir + 'qzv_results/demux/{runID}_' + demux_param + '.qzv',runID=RUN_IDS),
            out_dir + 'qzv_results/table/final_filt_' + demux_param + '.qzv',
            out_dir + 'qzv_results/repseq/final_' + demux_param + '.qzv',
            out_dir + 'qza_results/core_metrics/rareifed_table.qza',
            out_dir + 'qzv_results/core_metrics/alpha_diversity_metadata.qzv',
            out_dir + 'qzv_results/core_metrics/rarefaction.qzv',
            expand(out_dir + 'qzv_results/taxonomy/' + classify_method + '_{ref}.qzv', ref=refDict.keys()),
            expand(out_dir + 'qzv_results/taxonomy/barplots_' + classify_method + '_{ref}.qzv', ref=refDict.keys())

# if report only = no
    # include: Snakefile_q2

# include: Snakefile_report

# TODO: think about adding check for minimum reads count per sample per flow cell (need more than 1 sample per flow cell passing min threshold for tab/rep seq creation) - either see if we can include via LIMS in the manifest, or use samtools(?)

rule check_manifest:
    '''Check manifest for detailed character/format Q2 reqs

    QIIME2 has very explicit requirements for the manifest file.
    This step helps to enforce those requirements by either correcting
    simple deviations or exiting with informative errors prior to
    attempts to start QIIME2-based analysis steps.

    NOTE: this manifest is currently not used anywhere.  ? SS: Will be used downstream!

    #TODO: assert column order/name requirements here?
    '''
    input:
        meta_man_fullpath
    output:
        out_dir + 'manifests/manifest_qiime2.tsv'
    params:
        o = out_dir,
        e = exec_dir
    shell:
        # 'source /etc/profile.d/modules.sh; module load perl/5.18.0;'
        'perl {params.e}Q2Manifest.pl {params.o} {input} {output}'

rule create_per_sample_Q2_manifest:
    '''Create a QIIME2-specific manifest file per-sample

    Q2 needs a manifest in the following format:
        sample-id,absolute-filepath,direction

    Note that these per-sample files will be combined on a per-run ID
    basis in the following step, in keeping with the DADA2 requirement
    to group samples by flow cell (run ID).
    '''
    input:
        fq1 = get_orig_r1_fq,
        fq2 = get_orig_r2_fq
    output:
        temp(out_dir + 'manifests/{sample}_Q2_manifest.txt')
    shell:
        'echo "{wildcards.sample},{input.fq1},forward" > {output};'
        'echo "{wildcards.sample},{input.fq2},reverse" >> {output}'

rule combine_Q2_manifest_by_runID:
    '''Combine Q2-specific manifests by run ID

    NOTE: This step will only be scalable to a certain extent.
    Given enough samples, you will hit the cli character limit when
    using cat {input}.  If projects exceed a reasonable size, refactor
    here.
    '''
    input:
        expand(out_dir + 'manifests/{sample}_Q2_manifest.txt', sample=sampleDict.keys())
    output:
        out_dir + 'manifests/{runID}_Q2_manifest.txt'
    shell:
        'cat {input} | awk \'BEGIN{{FS=OFS="/"}}NR==1{{print "sample-id,absolute-filepath,direction"}}$9=="{wildcards.runID}"{{print $0}}\' > {output}'

rule create_symlinks:
    '''Symlink the original fastqs in an area that PIs can access

    TODO: Note that I've changed the directory structure from an earlier
    version.  Update documentation.
    '''
    input:
        fq1 = get_orig_r1_fq,
        fq2 = get_orig_r2_fq
    output:
        sym1 = out_dir + 'fastqs/' + '{sample}_R1.fastq.gz',
        sym2 = out_dir + 'fastqs/' + '{sample}_R2.fastq.gz'
    shell:
        'ln -s {input.fq1} {output.sym1};'
        'ln -s {input.fq2} {output.sym2}'

rule import_fastq_to_qza:
    '''
    Why did the bash script name things via runID instead of sample? SS: DADA2 requirement
    RunID pulls up multiple pairs of fastqs.  Are they meant to be combined? SS: Yes
    If they are, can we just combine at the fastq level?
    Does Q2 somehow combine everything in a given manifest, and that's the problem?
    Simple enough to create multiple manifests.

    If data is multiplexed, this step would de-~.  But, our data is already demultiplexed.
    provdes summaries and plots per flow cell (as QZA - not human-readable).

    Summary files are created for each flowcell (run ID) in QZA format. QZA files are
    QIIME2 artifacts that contain the QIIME2 parameters used to run the current step of the pipeline.
    They are meant to allow the user to repeat parts of the pipeline if you didn't have a
    workflow or other such documentation.
    '''
    input:
        out_dir + 'manifests/{runID}_Q2_manifest.txt'
    output:
        out_dir + 'qza_results/demux/{runID}_' + demux_param + '.qza'
    params:
        in_type = input_type,
        phred = phred_score,
        cmd_flag = 'source-format' if Q2_2017 else 'input-format'
    shell:
        'qiime tools import \
            --type {params.in_type} \
            --input-path {input} \
            --output-path {output} \
            --{params.cmd_flag} PairedEndFastqManifestPhred{params.phred}'

rule demux_visualization_qzv:
    '''
    The human-readble version of QZA files are QZV files, created in this step. QZV files can be viewed at
    www.view.qiime2.org
    '''
    input:
        out_dir + 'qza_results/demux/{runID}_' + demux_param + '.qza'
    output:
        out_dir + 'qzv_results/demux/{runID}_' + demux_param + '.qzv'
    shell:
        'qiime demux summarize \
            --i-data {input} \
            --o-visualization {output}'

if denoise_method in ['dada2', 'DADA2']:
    if Q2_2017:
        rule dada2_denoise:
            '''
            Generates feature tables and feature sequences. Each feature in the table is represented by one sequence (joined paired-end).
            QIIME 2017.10 does not require that both the table and sequences are generated in one step, however, QIIME 2019 does require
            they are generated together.

            SS: do we want to have the trimming be config features? We are giving it already demultiplexed data, so we don't need to trim
            but if PI's are using on external data, we may want to add that feature.
            '''
            input:
                qza = out_dir + 'qza_results/demux/{runID}_' + demux_param + '.qza'
            output:
                tab = out_dir + 'qza_results/table/{runID}_' + demux_param + '.qza',
                seq = out_dir + 'qza_results/repseq/{runID}_' + demux_param + '.qza'
            params:
                trim_l_f = trim_left_f,
                trim_l_r = trim_left_r,
                trun_len_f = trunc_len_f,
                trun_len_r = trunc_len_r
            threads: 8
            run:
                shell('qiime dada2 denoise-paired \
                    --p-n-threads {threads} \
                    --i-demultiplexed-seqs {input.qza} \
                    --o-table {output.tab} \
                    --o-representative-sequences {output.seq} \
                    --p-trim-left-f {params.trim_l_f} \
                    --p-trim-left-r {params.trim_l_r} \
                    --p-trunc-len-f {params.trun_len_f} \
                    --p-trunc-len-r {params.trun_len_r}')

    elif not Q2_2017:
        rule dada2_denoise:
            '''
            Generates feature tables and feature sequences. Each feature in the table is represented by one sequence (joined paired-end).
            QIIME 2017.10 does not require that both the table and sequences are generated in one step, however, QIIME 2019 does require
            they are generated together.

            SS: do we want to have the trimming be config features? We are giving it already demultiplexed data, so we don't need to trim
            but if PI's are using on external data, we may want to add that feature.
            '''
            input:
                qza = out_dir + 'qza_results/demux/{runID}_' + demux_param + '.qza'
            output:
                tab = out_dir + 'qza_results/table/{runID}_' + demux_param + '.qza',
                seq = out_dir + 'qza_results/repseq/{runID}_' + demux_param + '.qza',
                stats = out_dir + 'qza_results/dada2/stats/{runID}_' + demux_param + '.qza'
            params:
                trim_l_f = trim_left_f,
                trim_l_r = trim_left_r,
                trun_len_f = trunc_len_f,
                trun_len_r = trunc_len_r
            threads: 8
            run:
                shell('qiime dada2 denoise-paired \
                    --p-n-threads {threads} \
                    --i-demultiplexed-seqs {input.qza} \
                    --o-table {output.tab} \
                    --o-representative-sequences {output.seq} \
                    --o-denoising-stats {output.stats} \
                    --p-trim-left-f {params.trim_l_f} \
                    --p-trim-left-r {params.trim_l_r} \
                    --p-trunc-len-f {params.trun_len_f} \
                    --p-trunc-len-r {params.trun_len_r}')

        rule dada2_stats_visualization:
            """Generating visualization for DADA2 stats by flowcell.
            """
            input:
                out_dir + 'qza_results/dada2/stats/{runID}_' + demux_param + '.qza'
            output:
                out_dir + 'qzv_results/dada2/stats/{runID}_' + demux_param + '.qzv'
            shell:
                'qiime metadata tabulate \
                    --m-input-file {input} \
                    --o-visualization {output}'



# to add in metadata, start here: plus re- run perl check!  Must have the qza results for samples 
rule table_merge_qza:
    '''
    This step will merge each of the individual flowcell feature tables into one
    final QZA file.

    NOTE: Future qiime2 versions allow for multiple tables to be given at
    one time, however, this version does not allow this and one must be given at
    a time. This is because pair-wise merging is not allowed with this version,
    as table_merge cannot run with duplicate sample names. Once upgrading to version
    2019, we can eliminate the sh script entirely and example below can be used.

    WZ tested Q2 2019.1 merging with a single flow cell.  Downstream files appear
    consistent, however the "merged" table is a slightly different size compared
    to the original table.  The most conservative approach seems to be only merge
    when there are >1 flow cells (run IDs).

    '''
    input:
        tables = expand(out_dir + 'qza_results/table/{runID}_' + demux_param + '.qza',runID=RUN_IDS),
        q2_man = out_dir + 'manifests/manifest_qiime2.tsv'
    output:
        out_dir + 'qza_results/table/final_' + demux_param + '.qza'
    params:
        demux_param = demux_param,
        tab_dir = out_dir + 'qza_results/table/',
        e = exec_dir
    run:
        if Q2_2017:
            shell('sh {params.e}table_repseq_merge.sh {params.tab_dir} {output}')
        elif len(RUN_IDS) == 1:
            shell('cp {input.tables} {output}')
        else:
            shell('qiime feature-table merge \
                --i-tables {input.tables} \
                --o-merged-table {output}')

rule repseq_merge_qza:
    '''
    This step will merge each of the individual flowcell repseq tables into one
    final QZA file.

    Same note as above applies, with example code listed below.
    '''
    input:
        repseqs = expand(out_dir + 'qza_results/repseq/{runID}_' + demux_param + '.qza',runID=RUN_IDS),
        q2_man = out_dir + 'manifests/manifest_qiime2.tsv'
    output:
        out_dir + 'qza_results/repseq/final_' + demux_param + '.qza'
    params:
        demux_param = demux_param,
        tab_dir = out_dir + 'qza_results/repseq/',
        e = exec_dir
    run:
        if Q2_2017:
            shell('sh {params.e}table_repseq_merge.sh {params.tab_dir} {output}')
        elif len(RUN_IDS) == 1:
            shell('cp {input.repseqs} {output}')
        else:
            shell('qiime feature-table merge-seqs \
                --i-tables {input.repseqs} \
                --o-merged-table {output}')

rule filter_reads:
    '''
    This step will filter out samples that have zero reads  (eg blanks or failed samples) from the final merged
    feature table. Necessary for downstream PhyloSeq manipulation

    # TODO: not present in 2019 workflow. check with weiyin.

    '''
    input:
        out_dir + 'qza_results/table/final_' + demux_param + '.qza'
    output:
        out_dir + 'qza_results/table/final_filt_' + demux_param + '.qza'
    params:
        f_min = filt_min
    shell:
        'qiime feature-table filter-samples \
            --i-table {input} \
            --p-min-features {params.f_min} \
            --o-filtered-table {output}'

rule table_summary_qzv:
    '''
    This will generate information on how many sequences are associated with each sample
    and with each feature, histograms of those distributions, and some related summary statistics
    in a human viewable format.

    '''
    input:
        out_dir + 'qza_results/table/final_filt_' + demux_param + '.qza'
    output:
        out_dir + 'qzv_results/table/final_filt_' + demux_param + '.qzv'
    params:
        q2 = qiime2_version,
        q2_man = out_dir + 'manifests/manifest_qiime2.tsv'
    shell:
        'qiime feature-table summarize \
            --i-table {input} \
            --o-visualization {output} \
            --m-sample-metadata-file {params.q2_man}'

        # 2019:
        # 'qiime feature-table summarize --i-table {input.table_dada2_merged_qza} --o-visualization {output.table_dada2_merged_qzv}
        # TODO: --m?

rule repseq_summary_qzv:
    '''
    This will generate a mapping of feature IDs to sequences, and provide links
    to easily BLAST each sequence against the NCBI nt database in a human viewable
    format.
    '''
    input:
        out_dir + 'qza_results/repseq/final_' + demux_param + '.qza'
    output:
        out_dir + 'qzv_results/repseq/final_' + demux_param + '.qzv'
    shell:
        'qiime feature-table tabulate-seqs \
            --i-data {input} \
            --o-visualization {output}'

if Q2_2017:
    rule seq_alignment:
        '''
        This will perform a multiple sequence alignment of the all sequence files
        '''
        input:
            out_dir + 'qza_results/repseq/final_' + demux_param + '.qza'
        output:
            out_dir + 'qza_results/phylogeny/aligned_repseq.qza'
        shell:
            'qiime alignment mafft \
                --i-sequences {input} \
                --o-alignment {output}'
        # TODO: not in 2019?

    rule seq_alignment_filt:
        '''
        This will filter the alignment to remove positions that are highly variable
        '''
        input:
            out_dir + 'qza_results/phylogeny/aligned_repseq.qza'
        output:
            out_dir + 'qza_results/phylogeny/aligned_repseq_masked.qza'
        shell:
            'qiime alignment mask \
                --i-alignment {input} \
                --o-masked-alignment {output}'

    rule phylo_tree_unrooted:
        '''
        This will apply FastTree to generate a phylogenetic tree from the masked alignment
        '''
        input:
            out_dir + 'qza_results/phylogeny/aligned_repseq_masked.qza'
        output:
            out_dir + 'qza_results/phylogeny/phylo_tree_unrooted.qza'
        shell:
            'qiime phylogeny fasttree \
                --i-alignment {input} \
                --o-tree {output}'

    rule phylo_tree_rooted:
        '''
        This will us  midpoint rooting to place the root of the tree at the midpoint
        of the longest tip-to-tip distance in the unrooted tree
        '''
        input:
            out_dir + 'qza_results/phylogeny/phylo_tree_unrooted.qza'
        output:
            out_dir + 'qza_results/phylogeny/phylo_tree_rooted.qza'
        shell:
            'qiime phylogeny midpoint-root \
                --i-tree {input} \
                --o-rooted-tree {output}'

if not Q2_2017:
    rule phylogenetic_tree:
        input:
            out_dir + 'qza_results/repseq/final_' + demux_param + '.qza'
            #'repseqs_dada2/' + 'repseqs_dada2' + '.qza'
        output:
            aligned_repseqs = out_dir + 'qza_results/phylogeny/aligned_repseq.qza',
            masked_aligned_repseqs = out_dir + 'qza_results/phylogeny/aligned_repseq_masked.qza',
            unrooted_tree = out_dir + 'qza_results/phylogeny/phylo_tree_unrooted.qza',
            rooted_tree = out_dir + 'qza_results/phylogeny/phylo_tree_rooted.qza'
        shell:
            'qiime phylogeny align-to-tree-mafft-fasttree \
                --i-sequences {input} \
                --o-alignment {output.aligned_repseqs} \
                --o-masked-alignment {output.masked_aligned_repseqs} \
                --o-tree {output.unrooted_tree} \
                --o-rooted-tree {output.rooted_tree}'

# possible site of entry if you want to change sampling depth threshold!
rule alpha_beta_diversity:
    '''
    This step will perform alpha and beta diversity analysis. This includes:
    - Vector of Faith PD values by sample
    - Vector of Observed OTUs values by sample
    - Vector of Shannon diversity values by sample
    - Vector of Pielou's evenness values by sample
    - Matrices of unweighted and weighted UniFrac distances, Jaccard distances,
        and Bray-Curtis distances between pairs of samples.
    - PCoA matrix computed from unweighted and weighted UniFrac distances, Jaccard distances,
        and Bray-Curtis distances between samples.
    - Emperor plot of the PCoA matrix computed from unweighted and weighted UniFrac, Jaccard,
        and Bray-Curtis.

    NOTE: For this step you can use the --output-dir parameter instead of writing
    out all of the outputs BUT QIIME2 wants to create this directory itself and
    won't overwrite the directory if it already exits. This leads to an error since
    Snakemake will make the dir first, and Q2 errors

    #SS: Is listing all the output files necessary ? Should we create a list of these files?
    Not sure if there is a better way

    https://docs.qiime2.org/2017.11/plugins/available/diversity/core-metrics-phylogenetic/

    BB: fine to err a little on the verbose side.  One workaround to this sort of thing
    is to have output: d = directory(/some/path), then in the shell section, start off with
    the command rm -r {output.d}; qiime... but obviously this method has drawbacks.

    Unifrac attempt with one sample causes this step to core dump:
    https://forum.qiime2.org/t/core-metrics-phylogenetic-crashed-free-invalid-next-size/8408/6
    # TODO: write a check and handle gracefully
    '''
    input:
        rooted_tree = out_dir + 'qza_results/phylogeny/phylo_tree_rooted.qza',
        tab_filt = out_dir + 'qza_results/table/final_filt_' + demux_param + '.qza',
        q2_man = out_dir + 'manifests/manifest_qiime2.tsv'
    output:
        rare = out_dir + 'qza_results/core_metrics/rareifed_table.qza',
        faith = out_dir + 'qza_results/core_metrics/faith.qza',
        obs = out_dir + 'qza_results/core_metrics/observed.qza',
        shan = out_dir + 'qza_results/core_metrics/shannon.qza',
        even = out_dir + 'qza_results/core_metrics/evenness.qza',
        unw_dist = out_dir + 'qza_results/core_metrics/unweighted_dist.qza',
        unw_pcoa = out_dir + 'qza_results/core_metrics/unweighted_pcoa.qza',
        unw_emp = out_dir + 'qzv_results/core_metrics/unweighted_emperor.qzv',
        w_dist = out_dir + 'qza_results/core_metrics/weighted_dist.qza',
        w_pcoa = out_dir + 'qza_results/core_metrics/weighted_pcoa.qza',
        w_emp = out_dir + 'qzv_results/core_metrics/weighted_emperor.qzv',
        jac_dist = out_dir + 'qza_results/core_metrics/jaccard_dist.qza',
        jac_pcoa = out_dir + 'qza_results/core_metrics/jaccard_pcoa.qza',
        jac_emp = out_dir + 'qzv_results/core_metrics/jaccard_emperor.qzv',
        bc_dist = out_dir + 'qza_results/core_metrics/bray-curtis_dist.qza',
        bc_pcoa = out_dir + 'qza_results/core_metrics/bray-curtis_pcoa.qza',
        bc_emp = out_dir + 'qzv_results/core_metrics/bray-curtis_emperor.qzv'
    params:
        samp_depth = sampling_depth
    shell:
        'qiime diversity core-metrics-phylogenetic \
            --i-phylogeny {input.rooted_tree} \
            --i-table {input.tab_filt} \
            --p-sampling-depth {params.samp_depth} \
            --m-metadata-file {input.q2_man} \
            --o-rarefied-table {output.rare} \
            --o-faith-pd-vector {output.faith} \
            --o-observed-otus-vector {output.obs} \
            --o-shannon-vector {output.shan} \
            --o-evenness-vector {output.even} \
            --o-unweighted-unifrac-distance-matrix {output.unw_dist} \
            --o-unweighted-unifrac-pcoa-results {output.unw_pcoa} \
            --o-unweighted-unifrac-emperor {output.unw_emp} \
            --o-weighted-unifrac-distance-matrix {output.w_dist} \
            --o-weighted-unifrac-pcoa-results {output.w_pcoa} \
            --o-weighted-unifrac-emperor {output.w_emp} \
            --o-jaccard-distance-matrix {output.jac_dist} \
            --o-jaccard-pcoa-results {output.jac_pcoa} \
            --o-jaccard-emperor {output.jac_emp} \
            --o-bray-curtis-distance-matrix {output.bc_dist} \
            --o-bray-curtis-pcoa-results {output.bc_pcoa} \
            --o-bray-curtis-emperor {output.bc_emp}'

rule alpha_diversity_summary:
    '''
    This generates a tabular view of the metadata in a human viewable format.
    '''
    input:
        obs = out_dir + 'qza_results/core_metrics/observed.qza',
        shan = out_dir + 'qza_results/core_metrics/shannon.qza',
        even = out_dir + 'qza_results/core_metrics/evenness.qza',
        faith = out_dir + 'qza_results/core_metrics/faith.qza'
    output:
        out_dir + 'qzv_results/core_metrics/alpha_diversity_metadata.qzv'
    params:
        q2 = qiime2_version
    shell:
        'qiime metadata tabulate \
            --m-input-file {input.obs} \
            --m-input-file {input.shan} \
            --m-input-file {input.even} \
            --m-input-file {input.faith} \
            --o-visualization {output}'
    # not in 2019 workflow - confirm that usage is the same

rule alpha_rarefaction:
    '''
    '''
    input:
        tab_filt = out_dir + 'qza_results/table/final_filt_' + demux_param + '.qza',
        rooted = out_dir + 'qza_results/phylogeny/phylo_tree_rooted.qza',
        q2_man = out_dir + 'manifests/manifest_qiime2.tsv'
    output:
        out_dir + 'qzv_results/core_metrics/rarefaction.qzv'
    params:
        m_depth = max_depth
    shell:
        'qiime diversity alpha-rarefaction \
            --i-table {input.tab_filt} \
            --i-phylogeny {input.rooted} \
            --p-max-depth {params.m_depth} \
            --m-metadata-file {input.q2_man} \
            --o-visualization {output}'

rule taxonomy_qza:
    '''
    Note that different classification methods have entirely different command
    line flags, so they will each need their own invocation.
    '''
    input:
        tab_filt = out_dir + 'qza_results/repseq/final_' + demux_param + '.qza',
        ref = get_ref_full_path
    output:
        out_dir + 'qza_results/taxonomy/' + classify_method + '_{ref}.qza'
    params:
        c_method = classify_method
    threads: 2
    run:
        if classify_method == 'classify-sklearn':
            shell('qiime feature-classifier {params.c_method} \
                --p-n-jobs {threads} \
                --i-classifier {input.ref} \
                --i-reads {input.tab_filt} \
                --o-classification {output}')

rule taxonomy_summary_qzv:
    '''
    '''
    input:
        out_dir + 'qza_results/taxonomy/' + classify_method + '_{ref}.qza'
    output:
        out_dir + 'qzv_results/taxonomy/' + classify_method + '_{ref}.qzv'
    shell:
        'qiime metadata tabulate \
            --m-input-file {input} \
            --o-visualization {output}'

rule taxonomy_barplots_qzv:
    '''
    '''
    input:
        tab_filt = out_dir + 'qza_results/table/final_filt_' + demux_param + '.qza',
        tax = out_dir + 'qza_results/taxonomy/' + classify_method + '_{ref}.qza',
        mani = out_dir + 'manifests/manifest_qiime2.tsv'
    output:
        out_dir + 'qzv_results/taxonomy/barplots_' + classify_method + '_{ref}.qzv'
    shell:
        'qiime taxa barplot \
            --i-table {input.tab_filt} \
            --i-taxonomy {input.tax} \
            --m-metadata-file {input.mani} \
            --o-visualization {output}'
