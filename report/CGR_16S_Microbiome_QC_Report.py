{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# to save report:\n",
    "    # clone the following repo: https://github.com/ihuston/jupyter-hide-code-html\n",
    "    # run in terminal: jupyter nbconvert --to html --template jupyter-hide-code-html/clean_output.tpl path/to/CGR_16S_Microbiome_QC_Report.ipynb\n",
    "    # name the above file NP###_pipeline_run_folder_QC_report.html and place it in the directory with the pipeline output\n",
    "    \n",
    "# for version control:\n",
    "    # Kernel > Restart & Clear Output\n",
    "    # run in terminal: jupyter nbconvert --to script CGR_16S_Microbiome_QC_Report.ipynb\n",
    "    # add/commit CGR_16S_Microbiome_QC_Report.ipynb AND CGR_16S_Microbiome_QC_Report.py to git"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CGR 16S Microbiome QC Report"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<!-- <div id=\"toc_container\"> -->\n",
    "<h2>Table of Contents</h2>\n",
    "<ul class=\"toc_list\">\n",
    "  <a href=\"#1&nbsp;&nbsp;General-analysis-information\">1&nbsp;&nbsp;General analysis information</a><br>\n",
    "  <ul>\n",
    "    <a href=\"#1.1&nbsp;&nbsp;Project-directory\">1.1&nbsp;&nbsp;Project directory</a><br>\n",
    "    <a href=\"#1.2&nbsp;&nbsp;Project-directory-contents\">1.2&nbsp;&nbsp;Project directory contents</a><br>\n",
    "    <a href=\"#1.3&nbsp;&nbsp;Parameters\">1.3&nbsp;&nbsp;Parameters</a><br>\n",
    "    <a href=\"#1.4&nbsp;&nbsp;Dependency-versions\">1.4&nbsp;&nbsp;Dependency versions</a><br>\n",
    "  </ul>\n",
    "  <a href=\"#2&nbsp;&nbsp;Samples-included-in-the-project\">2&nbsp;&nbsp;Samples included in the projec<br>\n",
    "  <a href=\"#3&nbsp;&nbsp;QC-checks\">3&nbsp;&nbsp;QC checks</a><br>\n",
    "  <ul>\n",
    "    <a href=\"#3.1&nbsp;&nbsp;Read-trimming\">3.1&nbsp;&nbsp;Read trimming</a><br>\n",
    "    <a href=\"#3.2&nbsp;&nbsp;Proportion-of-non-bacterial-reads\">3.2&nbsp;&nbsp;Proportion of non-bacterial reads<br>\n",
    "    <ul>\n",
    "      <a href=\"#3.2.1&nbsp;&nbsp;Proportion-of-non-bacterial-reads-per-sample-type\">3.2.1&nbsp;&nbsp;Proportion of non-bacterial reads per sample type<br>\n",
    "    </ul>\n",
    "    <a href=\"#3.3&nbsp;&nbsp;Sequencing-depth-distribution-per-flow-cell\">3.3&nbsp;&nbsp;Sequencing distribution per flow cell</a><br>\n",
    "    <a href=\"#3.4&nbsp;&nbsp;Read-counts-after-filtering-in-blanks-vs.-study-samples\">3.4&nbsp;&nbsp;Read counts after filtering in blanks vs. study samples</a><br>\n",
    "    <a href=\"#3.5&nbsp;&nbsp;Biological-replicates\">3.5&nbsp;&nbsp;Biological replicates</a><br>\n",
    "    <a href=\"#3.6&nbsp;&nbsp;QC-samples\">3.6&nbsp;&nbsp;QC samples</a><br>\n",
    "  </ul>\n",
    "  <a href=\"#4&nbsp;&nbsp;Rarefaction-threshold\">4&nbsp;&nbsp;Rarefaction threshold</a><br>\n",
    "  <a href=\"#5&nbsp;&nbsp;Alpha-diversity\">5&nbsp;&nbsp;Alpha diversity</a><br>\n",
    "  <a href=\"#6&nbsp;&nbsp;Beta-diversity\">6&nbsp;&nbsp;Beta diversity</a><br>\n",
    "  <ul>\n",
    "    <a href=\"#6.1&nbsp;&nbsp;Bray-Curtis\">6.1&nbsp;&nbsp;Bray-Curtis</a><br>\n",
    "    <a href=\"#6.2&nbsp;&nbsp;Jaccard\">6.2&nbsp;&nbsp;Jaccard</a><br>\n",
    "    <a href=\"#6.3&nbsp;&nbsp;Weighted-UniFrac\">6.3&nbsp;&nbsp;Weighted UniFrac</a><br>\n",
    "    <a href=\"#6.4&nbsp;&nbsp;Unweighted-UniFrac\">6.4&nbsp;&nbsp;Unweighted UniFrac</a><br>\n",
    "  </ul>\n",
    "</ul>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"1&nbsp;&nbsp;General-analysis-information\">1&nbsp;&nbsp;General analysis information</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"1.1&nbsp;&nbsp;Project-directory\">1.1&nbsp;&nbsp;Project directory</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "All production microbiome projects are located in `/DCEG/Projects/Microbiome/Analysis/`.  There is a parent folder named with the project ID; that folder contains the [bioinformatic pipeline](https://github.com/NCI-CGR/QIIME_pipeline) runs for that project and a `readme` summarizing the changes between each run.  \n",
    "\n",
    "- The initial run (always named `<datestamp>_initial_run`) is used for some QC checks and to evaluate parameter settings.  \n",
    "- The second run implements additional read trimming and excludes water blanks, no-template controls, and QC samples (e.g. robogut or artificial colony samples).  (NOTE: pick one of intentional dups?)\n",
    "- Additional runs are performed for study-specific reasons which are summarized in the `readme`.\n",
    "<br><br>\n",
    "\n",
    "__The project and pipeline run described in this report is located here:__"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# proj_dir='/DCEG/Projects/Microbiome/Analysis/Project_NP0493-MB2/20200221_initial_run'\n",
    "# proj_dir='/DCEG/Projects/Microbiome/Analysis/Project_NP0539-MB1/20200306_initial_run'\n",
    "# proj_dir='/DCEG/Projects/Microbiome/Analysis/Project_NP0539-MB1/20200306_reads_trimmed_blanks_excluded'\n",
    "proj_dir='/DCEG/Projects/Microbiome/Analysis/Project_NP0539-MB1/20200320_reads_trimmed_blanks_and_qc_excluded'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%cd {proj_dir}"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The contents of the `readme`, at the time of report generation:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!cat ../README"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"1.2&nbsp;&nbsp;Project-directory-contents\">1.2&nbsp;&nbsp;Project directory contents</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!ls"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"1.3&nbsp;&nbsp;Parameters\">1.3&nbsp;&nbsp;Parameters</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!cat *.yml"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"1.4&nbsp;&nbsp;Dependency-versions\">1.4&nbsp;&nbsp;Dependency versions</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!cat Q2_wrapper.sh.o*"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"2&nbsp;&nbsp;Samples-included-in-the-project\">2&nbsp;&nbsp;Samples included in the project</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The tables below show the count of samples grouped by metadata provided in the manifest."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from IPython.display import display\n",
    "import os.path\n",
    "%matplotlib inline\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib as mpl\n",
    "import seaborn as sns\n",
    "import glob\n",
    "from skbio.stats.ordination import pcoa\n",
    "from skbio import DistanceMatrix\n",
    "\n",
    "sns.set(style=\"whitegrid\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "manifest = pd.read_csv(glob.glob('*.txt')[0],sep='\\t',index_col=0)\n",
    "manifest.columns = map(str.lower, manifest.columns)\n",
    "manifest = manifest.dropna(how='all', axis='columns')\n",
    "manifest.columns = manifest.columns.str.replace(' ', '')  # remove once cleaning is implemented in the pipeline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "manifest['Sequencer'] = (manifest['run-id'].str.split('_',n=2,expand=True))[1]\n",
    "if 'sourcepcrplate' in manifest.columns:\n",
    "    manifest['PCR_plate'] = (manifest['sourcepcrplate'].str.split('_',n=1,expand=True))[0]\n",
    "else:\n",
    "    print(\"Source PCR Plate column not detected in manifest.\")\n",
    "# should probably save this file, or even better, include in original manifest prior to analysis...."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "m = manifest.drop(columns=['externalid','sourcepcrplate','project-id','extractionbatchid','fq1','fq2'],errors='ignore')\n",
    "# when do we want to drop extraction ID?  in this case, it's all unique values for QC samples and NaNs for study samples\n",
    "# possibly look for (# unique values == # non-nan values) instead of alßways dropping\n",
    "\n",
    "for i in m.columns:\n",
    "    display(m[i].value_counts().rename_axis(i).to_frame('Number of samples'))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"3&nbsp;&nbsp;QC-checks\">3&nbsp;&nbsp;QC checks</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.1&nbsp;&nbsp;Read-trimming\">3.1&nbsp;&nbsp;Read trimming</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The trimming parameters for the initial pipeline run (`<datestamp>_initial_run`) are set to 0 (no trimming).  For subsequent runs, trimming parameters are set based on the read quality plots (not shown here; please browse `import_and_demultiplex/<runID>.qzv` using [QIIME's viewer](https://view.qiime2.org/) for quality plots).  For this run, trimming parameters (also found in the config) are as follows:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!grep -A4 \"dada2_denoise\" *.yml"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.2&nbsp;&nbsp;Proportion-of-non-bacterial-reads\">3.2&nbsp;&nbsp;Proportion of non-bacterial reads</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "After error correction, chimera removal, and removal of phiX sequences, the remaining reads are used for taxonomic classification.  We are performing classification with a naive Bayes classifier trained on the SILVA 99% OTUs database that includes only the V4 region (defined by the 515F/806R primer pair).  This data is located at `taxonomic_classification/barplots_classify-sklearn_silva-132-99-515-806-nb-classifier.qzv`.  Please use [QIIME's viewer](https://view.qiime2.org/) for a more detailed interactive plot.\n",
    "\n",
    "The plots below show the \"level 1\" taxonomic classification.  The first plot shows relative abundances; the second shows absolute.\n",
    "\n",
    "Note that reads are being classified using a database of predominantly bacterial sequences, so human reads, for example, will generally be in the \"Unclassified\" category rather than \"Eukaryota.\"  Non-bacterial reads can indicate host (human) or other contamination. \n",
    "\n",
    "_Best practices indicate we should filter these reads regardless of the degree to which we observe them; this feature is in development and will be available in release 2.1._"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!unzip -q -d taxonomic_classification/rpt_silva taxonomic_classification/barplots_classify-sklearn_silva-132-99-515-806-nb-classifier.qzv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "f = glob.glob('taxonomic_classification/rpt_silva/*/data/level-1.csv')\n",
    "df_l1 = pd.read_csv(f[0])\n",
    "df_l1 = df_l1.rename(columns = {'index':'Sample'})\n",
    "df_l1 = df_l1.set_index('Sample')\n",
    "df_l1 = df_l1.select_dtypes(['number']).dropna(axis=1, how='all')\n",
    "df_l1_rel = df_l1.div(df_l1.sum(axis=1), axis=0) * 100"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(dpi=200)\n",
    "pal = sns.color_palette(\"Accent\")\n",
    "ax = df_l1_rel.sort_values('D_0__Bacteria').plot.bar(stacked=True, color=pal, figsize=(60,7), width=1, edgecolor='white', ax=plt.gca())\n",
    "ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.5),ncol=4,fontsize=52)\n",
    "ax.set_ylabel('Relative frequency (%)',fontsize=52)\n",
    "ax.set_title('Taxonomic classification, level 1',fontsize=52)\n",
    "ax.set_yticklabels(ax.get_yticks(), size = 40)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(dpi=200)\n",
    "pal = sns.color_palette(\"Accent\")\n",
    "ax = df_l1.sort_values('D_0__Bacteria').plot.bar(stacked=True, color=pal, figsize=(60,7), width=1, edgecolor='white', ax=plt.gca())\n",
    "ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.5),ncol=4,fontsize=52)\n",
    "ax.set_ylabel('Absolute frequency',fontsize=52)\n",
    "ax.set_title('Taxonomic classification, level 1',fontsize=52)\n",
    "ax.set_yticklabels(ax.get_yticks(), size = 40)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h4 id=\"3.2.1&nbsp;&nbsp;Proportion-of-non-bacterial-reads-per-sample-type\">3.2.1&nbsp;&nbsp;Proportion of non-bacterial reads per sample type</h4>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This section highlights non-bacterial reads in various sub-populations included in the study (e.g. study samples, robogut or artificial control samples, and blanks).  This can be helpful with troubleshooting if some samples unexpectedly have a high proportion of non-bacterial reads."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_level_1_subpops(samples,pop):\n",
    "    plt.rcParams[\"xtick.labelsize\"] = 12\n",
    "    n = -0.5\n",
    "    r = 90\n",
    "    ha = \"center\"\n",
    "    f = 12\n",
    "    if len(samples) < 30:\n",
    "        plt.rcParams[\"xtick.labelsize\"] = 40\n",
    "        n = -0.8\n",
    "        r = 40\n",
    "        ha = \"right\"\n",
    "        f = 40\n",
    "    plt.figure(dpi=200)\n",
    "    pal = sns.color_palette(\"Accent\")\n",
    "    ax = df_l1_rel[df_l1_rel.index.isin(samples)].sort_values('D_0__Bacteria').plot.bar(stacked=True, color=pal, figsize=(60,7), width=1, edgecolor='white', ax=plt.gca())\n",
    "    ax.legend(loc='upper center', bbox_to_anchor=(0.5, n),ncol=4,fontsize=52)\n",
    "    ax.set_ylabel('Relative frequency (%)',fontsize=52)\n",
    "    ax.set_xlabel('Sample',fontsize=f)\n",
    "    ax.set_title('Taxonomic classification, level 1, ' + pop + ' samples only',fontsize=52)\n",
    "    ax.set_yticklabels(ax.get_yticks(), size = 40)\n",
    "    ax.set_xticklabels(ax.get_xticklabels(), rotation=r, ha=ha)\n",
    "    plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if 'sampletype' in manifest.columns:\n",
    "    for i in manifest['sampletype'].unique():\n",
    "        l = list(manifest[manifest['sampletype'].str.match(i)].index)\n",
    "        plot_level_1_subpops(l,i)\n",
    "else:\n",
    "    print(\"No Sample Type column detected in manifest.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.3&nbsp;&nbsp;Sequencing-depth-distribution-per-flow-cell\">3.3&nbsp;&nbsp;Sequencing depth distribution per flow cell</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Per-sample read depths are recorded in `import_and_demultiplex/<runID>.qzv`.  Those values are plotted below, excluding NTC and water blanks.  Distributions per flow cell should be similar if the flow cells contained the same number of non-blank samples.  If a flow cell contains fewer samples, each sample will have a greater number of reads, so that the total number of reads produced per flow cell remains approximately the same."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%%bash\n",
    "cd import_and_demultiplex\n",
    "for i in *qzv; do unzip -q $i -d \"rpt_${i%.*}\"; done\n",
    "for i in rpt_*/*/data/per-sample-fastq-counts.csv; do j=${i%%/*}; k=${j#\"rpt_\"}; awk -v var=\"$k\" 'BEGIN{FS=\",\";OFS=\"\\t\"}$1!~/Sample name/{print $1,$2,var}' $i >> t; done\n",
    "cat <(echo -e \"Sample_name\\tSequence_count\\tRun_ID\") t > rpt_vertical_per-sample-fastq-counts.csv\n",
    "rm t\n",
    "cd .."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_depth = pd.read_csv('import_and_demultiplex/rpt_vertical_per-sample-fastq-counts.csv',sep='\\t')\n",
    "search_values = ['Water','NTC']\n",
    "df_depth_no_blanks = df_depth[~df_depth.Sample_name.str.contains('|'.join(search_values ),case=False)]\n",
    "plt.figure(dpi=100)\n",
    "sns.set(style=\"whitegrid\")\n",
    "ax = sns.boxplot(x=\"Run_ID\",y=\"Sequence_count\",data=df_depth_no_blanks)\n",
    "ax.set_xticklabels(ax.get_xticklabels(),rotation=40,ha=\"right\")#,fontsize=8)\n",
    "ax.axes.set_title(\"Sequencing depth distribution per flow cell\",fontsize=12)\n",
    "# ax.tick_params(labelsize=8)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.4&nbsp;&nbsp;Read-counts-after-filtering-in-blanks-vs.-study-samples\">3.4&nbsp;&nbsp;Read counts after filtering in blanks vs. study samples</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Per-sample read depths at each filtering step are recorded in `denoising/stats/<runID>.qzv`.  The plots below show the mean for each category; error bars indicate the 95% confidence interval.  \n",
    "\n",
    "NTC blanks are expected to have near-zero read depths, and represent false positives introduced by sequencing reagents.  \n",
    "\n",
    "Water blanks are expected to have read depths that are at least one to two orders of magnitude lower than the average study sample depth.  They represent the relatively low level of taxa that may be detected in the water used in the lab."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%%bash\n",
    "cd denoising/stats/\n",
    "for i in *qzv; do unzip -q $i -d \"rpt_${i%.*}\"; done\n",
    "for i in rpt_*/*/data/metadata.tsv; do dos2unix -q $i; j=${i%%/*}; k=${j#\"rpt_\"}; awk -v var=\"$k\" 'BEGIN{FS=OFS=\"\\t\"}NR>2{print $0,var}' $i >> t; done\n",
    "cat <(echo -e \"sample-id\\tinput\\tfiltered\\tdenoised\\tmerged\\tnon-chimeric\\tflow_cell\") t > rpt_denoising_stats.tsv\n",
    "rm t\n",
    "cd ../.."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_stats = pd.read_csv('denoising/stats/rpt_denoising_stats.tsv',sep='\\t')\n",
    "df_stats = df_stats.set_index('sample-id')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_read_counts(samples,pop):\n",
    "    plt.figure(dpi=100)\n",
    "    sns.set(style=\"whitegrid\")\n",
    "    ax = sns.barplot(data=df_stats[df_stats.index.isin(samples)]).set_title('Number of reads in ' + pop + ' samples')\n",
    "    plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "if 'sampletype' in manifest.columns:\n",
    "    for i in manifest['sampletype'].unique():\n",
    "        l = list(manifest[manifest['sampletype'].str.match(i)].index)\n",
    "        plot_read_counts(l,i)\n",
    "else:\n",
    "    print(\"No Sample Type column detected in manifest.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The table below shows the 30 samples with the lowest non-chimeric read counts.  This information may be helpful in identifying problematic samples and determining a minimum read threshold for sample inclusion.  Note that low-depth study samples will be excluded from diversity analysis based on the sampling depth threshold selected (discussed in the following section)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if 'externalid' in manifest.columns:\n",
    "    display(df_stats.join(manifest[['externalid']])[['externalid','input','filtered','denoised','merged','non-chimeric']].sort_values(['non-chimeric']).head(30))\n",
    "else:\n",
    "    display(df_stats[['input','filtered','denoised','merged','non-chimeric']].sort_values(['non-chimeric']).head(30))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.5&nbsp;&nbsp;Biological-replicates\">3.5&nbsp;&nbsp;Biological replicates</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Paired duplicates, for the purposes of this pipeline, are defined by an identical \"ExternalID.\"  The taxonomic classification (using the SILVA 99% OTUs database) at levels 2 through 7 are compared across each pair and evaluated using cosine similarity.  The closer the cosine similarity value is to 1, the more similar the vectors are."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "manifest_no_blanks = manifest[~manifest.index.str.contains('|'.join(['Water','NTC']),case=False)]\n",
    "if 'externalid' in manifest_no_blanks.columns:\n",
    "    dup1_sample = list(manifest_no_blanks[manifest_no_blanks.duplicated(subset='externalid', keep='first')].sort_values('externalid').index)\n",
    "    dup2_sample = list(manifest_no_blanks[manifest_no_blanks.duplicated(subset='externalid', keep='last')].sort_values('externalid').index)\n",
    "    l = dup1_sample + dup2_sample\n",
    "else:\n",
    "    print(\"No External ID column detected in manifest.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def compare_replicates(f,l):\n",
    "    df = pd.read_csv(f[0])\n",
    "    df = df.rename(columns = {'index':'Sample'})\n",
    "    df = df.set_index('Sample')\n",
    "    df_dups = df[df.index.isin(l)]\n",
    "    df_dups = df_dups.select_dtypes(['number']).dropna(axis=1, how='all')\n",
    "    return df_dups"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from scipy.spatial.distance import cosine"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "ids_list = []\n",
    "if 'externalid' in manifest_no_blanks.columns:\n",
    "    for a, b in zip(dup1_sample, dup2_sample):\n",
    "        ids = [manifest.loc[a,'externalid'], a, b]\n",
    "        ids_list.append(ids)\n",
    "    df_cosine = pd.DataFrame(ids_list, columns=['externalid','replicate_1','replicate_2'])\n",
    "\n",
    "    levels = [2,3,4,5,6,7]\n",
    "    for n in levels:\n",
    "        cos_list = []\n",
    "        f = glob.glob('taxonomic_classification/rpt_silva/*/data/level-' + str(n) + '.csv')\n",
    "        df_dups = compare_replicates(f, l)\n",
    "        for a, b in zip(dup1_sample, dup2_sample):\n",
    "            cos_list.append(1 - cosine(df_dups.loc[a,],df_dups.loc[b,]))\n",
    "        df_cosine['level_' + str(n)] = cos_list\n",
    "    display(df_cosine)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if 'externalid' in manifest_no_blanks.columns:\n",
    "    if (df_cosine.drop(columns=['externalid','replicate_1','replicate_2']) < 0.99 ).any().any():\n",
    "        print(\"Some biological replicates have cosine similarity below 0.99.\")\n",
    "    else:\n",
    "        print(\"At all levels of taxonomic classification, the biological replicate samples have cosine similarity of at least 0.99.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"3.6&nbsp;&nbsp;QC-samples\">3.6&nbsp;&nbsp;QC samples</h3>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "If robogut and/or artificial colony samples are included in the analysis, then the distributions of relative abundances in each sample at classification levels 2 through 6 are shown here.  This illustrates the variability between samples within each QC population with regard to taxonomic classification."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "ac_samples = []\n",
    "rg_samples = []\n",
    "if 'sampletype' in manifest.columns:\n",
    "    ac_samples = list(manifest[manifest['sampletype'].str.lower().isin(['artificialcolony','artificial colony'])].index)\n",
    "    rg_samples = list(manifest[manifest['sampletype'].str.lower().isin(['robogut'])].index)\n",
    "else:\n",
    "    print(\"No Sample Type column detected in manifest.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_rel_abundances_in_QCs(samples,qc_pop):\n",
    "    levels = [2,3,4,5,6]\n",
    "    for n in levels:\n",
    "        f = glob.glob('taxonomic_classification/rpt_silva/*/data/level-' + str(n) + '.csv')\n",
    "        df = pd.read_csv(f[0],index_col=0)\n",
    "        df = df[df.index.isin(samples)]\n",
    "        df = df.select_dtypes(['number']).dropna(axis=1, how='all').loc[:,~(df==0.0).all(axis=0)]\n",
    "        df_rel = df.div(df.sum(axis=1), axis=0) * 100\n",
    "        plt.figure(dpi=150) \n",
    "        ax = df_rel.boxplot()\n",
    "        ax.set_xticklabels(ax.get_xticklabels(),rotation=90,fontsize=8)\n",
    "        ax.set_title('Distribution of relative abundances in ' + qc_pop + ', level ' + str(n))\n",
    "        plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "if ac_samples:\n",
    "    plot_rel_abundances_in_QCs(ac_samples,'artificial colony')\n",
    "else:\n",
    "    print(\"No artificial colony samples were included in this pipeline run.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "if rg_samples:\n",
    "    plot_rel_abundances_in_QCs(rg_samples,'robogut')\n",
    "else:\n",
    "    print(\"No robogut samples were included in this pipeline run.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"4&nbsp;&nbsp;Rarefaction-threshold\">4&nbsp;&nbsp;Rarefaction threshold</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "QIIME randomly subsamples the reads per sample, without replacement, up to the sampling depth parameter.  Samples with reads below the sampling depth are excluded from analysis.  A higher sampling depth will include more reads overall, but will also exclude more samples.\n",
    "\n",
    "Our default sampling depth is 10,000, which is the setting for the initial pipeline run (`<datestamp>_initial_run`).  The information provided in this section may be used to fine tune the sampling depth for subsequent runs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!unzip -q -d denoising/feature_tables/rpt_merged_filtered_qzv denoising/feature_tables/merged_filtered.qzv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_features_per_samples = pd.read_csv(glob.glob('denoising/feature_tables/rpt_merged_filtered_qzv/*/data/sample-frequency-detail.csv')[0],sep=\",\",header=None,index_col=0)\n",
    "if 'externalid' in manifest.columns:\n",
    "    df_features_per_samples = df_features_per_samples.join(manifest[['externalid']]).set_index('externalid')\n",
    "sample_ttl = len(df_features_per_samples.index)\n",
    "feature_ttl = df_features_per_samples[1].sum()\n",
    "blank_ttl = len(df_features_per_samples[df_features_per_samples.index.str.contains('Water|NTC',case=False)])\n",
    "values = [5000,10000,15000,20000,25000,30000,35000,40000]\n",
    "samples = []\n",
    "features = []\n",
    "blanks = []\n",
    "ids = []\n",
    "for n in values:\n",
    "    df_temp = df_features_per_samples[df_features_per_samples[1] > n]\n",
    "    l = df_features_per_samples[df_features_per_samples[1] <= n].index.to_list()\n",
    "    l.sort()\n",
    "    ids.append(l)\n",
    "    samples_left = len(df_temp.index)\n",
    "    blanks_left = len(df_temp[df_temp.index.str.contains('Water|NTC',case=False)])\n",
    "    samples.append(samples_left/sample_ttl * 100)\n",
    "    features.append((samples_left * n)/feature_ttl * 100)\n",
    "    if blank_ttl != 0:\n",
    "        blanks.append(blanks_left/blank_ttl * 100)\n",
    "    else:\n",
    "        blanks.append(\"NA\")\n",
    "df_rarify = pd.DataFrame(list(zip(values, samples, features, ids, blanks)),columns=['Sampling_depth','Percent_retained_samples','Percent_retained_seqs','Samples_excluded','Percent_retained_blanks'])\n",
    "df_rarify = df_rarify.set_index('Sampling_depth')\n",
    "pd.set_option('display.max_colwidth', 0)\n",
    "df_rarify[['Samples_excluded','Percent_retained_samples','Percent_retained_blanks']]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_rarify_tidy = df_rarify.reset_index().drop(columns=['Samples_excluded','Percent_retained_blanks']).melt(id_vars='Sampling_depth')\n",
    "df_rarify_tidy.columns = ['Sampling_depth','Var','Percent_retained']\n",
    "df_rarify_tidy['Var'] = df_rarify_tidy['Var'].str.replace('Percent_retained_s','S')\n",
    "plt.figure(dpi=120)\n",
    "ax = sns.lineplot(x=\"Sampling_depth\", y=\"Percent_retained\", hue=\"Var\",data=df_rarify_tidy)\n",
    "handles, labels = ax.get_legend_handles_labels()\n",
    "ax.legend(handles=handles[1:], labels=labels[1:], loc='center left', bbox_to_anchor=(1, 0.5))\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "For this pipeline run, the rarefaction depth was set in the config file as follows:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!grep \"sampling_depth\" *.yml"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"5&nbsp;&nbsp;Alpha-diversity\">5&nbsp;&nbsp;Alpha diversity</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Alpha diversity measures species richness, or variance within a sample.\n",
    "\n",
    "The rarefaction curves below show the number of species as a function of the number of samples.  The various plots are stratified by the metadata available in the manifest.  The curves are expected to grow rapidly as common species are identified, then plateau as only the rarest species remain to be sampled.  The rarefaction threshold discussed above should fall within the plateau of the rarefaction curves.\n",
    "\n",
    "This report provides the following alpha diversity metrics:\n",
    "- __Observed OTUs:__ represents the number of observed species for each class\n",
    "- __Shannon diversity index:__ Calculates richness and diversity using a natural logarithm; accounts for both abundance and evenness of the taxa present; more sensitive to species richness than evenness\n",
    "- __Faith's phylogenetic diversity:__ Measure of biodiversity that incorporates phylogenetic difference between species via sum of length of branches"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!unzip -q -d diversity_core_metrics/rpt_rarefaction diversity_core_metrics/rarefaction.qzv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "def format_alpha_data(metric, csv):\n",
    "    df = pd.read_csv(csv,index_col=0)\n",
    "    df.columns = map(str.lower, df.columns)\n",
    "    depth_cols = [col for col in df.columns if 'depth-' in col]\n",
    "    non_depth_cols = [col for col in df.columns if 'depth-' not in col]\n",
    "    depths = list(set([i.split('_', 1)[0] for i in depth_cols]))\n",
    "    iters = list(set([i.split('_', 1)[1] for i in depth_cols]))\n",
    "    df_melt1 = pd.DataFrame()\n",
    "    df_melt2 = pd.DataFrame()\n",
    "    for d in depths:\n",
    "        df_temp = df.filter(regex=d+'_')\n",
    "        df_temp.columns = iters\n",
    "        df_temp = pd.concat([df_temp,df[non_depth_cols]],axis=1)\n",
    "        df_temp['depth'] = int(d.split('-')[1])\n",
    "        df_melt1 = pd.concat([df_melt1,df_temp],axis=0)\n",
    "    non_depth_cols.append('depth')\n",
    "    for i in iters:\n",
    "        df_temp = df_melt1.filter(regex='^' + i + '$')\n",
    "        df_temp.columns = [metric]\n",
    "        df_temp = pd.concat([df_temp,df_melt1[non_depth_cols]],axis=1)\n",
    "        df_temp['iteration'] = int(i.split('-')[1])\n",
    "        df_melt2 = pd.concat([df_melt2,df_temp],axis=0)\n",
    "    return df_melt2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "mpl.rcParams['figure.max_open_warning'] = 40\n",
    "files = glob.glob('diversity_core_metrics/rpt_rarefaction/*/data/*.csv')\n",
    "for f in files:\n",
    "    b = os.path.basename(f).split('.')[0]\n",
    "    df = format_alpha_data(b, f)\n",
    "    df.columns = df.columns.str.replace(' ', '')  # temporary - remove once cleaning is implemented in the pipeline\n",
    "    df['Sequencer'] = (df['run-id'].str.split('_',n=2,expand=True))[1]\n",
    "    if 'sourcepcrplate' in df.columns:\n",
    "        df['PCR_plate'] = (df['sourcepcrplate'].str.split('_',n=1,expand=True))[0]\n",
    "    df['run-id'] = (df['run-id'].str.split('-',expand=True)[1])\n",
    "    # should probably save this file, or even better, include in original manifest prior to analysis....\n",
    "    cols = df.columns.drop([b,'depth','iteration','sourcepcrplate','externalid','extractionbatchid','fq1','fq2'],errors='ignore')\n",
    "    for c in cols:\n",
    "        plt.figure(dpi=130)\n",
    "        ax = sns.lineplot(x=\"depth\", y=b, hue=c, err_style=\"band\", data=df)\n",
    "        handles, labels = ax.get_legend_handles_labels()\n",
    "        ax.legend(handles=handles[1:], labels=labels[1:], loc='center left', bbox_to_anchor=(1, 0.5))\n",
    "        ax.set_title('Rarefaction curves by ' + c)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h2 id=\"6&nbsp;&nbsp;Beta-diversity\">6&nbsp;&nbsp;Beta diversity</h2>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The data displayed here is mainly for use in evaluating potential confounders (e.g. flow cell, sequencer, etc.).  For convenience, we have included the PCoA plots for all metadata provided; however, we strongly encourage the use of [EMPeror](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4076506/), available through [QIIME's viewer](https://view.qiime2.org/), for further project analysis.\n",
    "\n",
    "Beta diversity measures variance across samples/environments.  \n",
    "\n",
    "The three-axis plots below show PCoA results for the first three components of several beta diversity metrics.  Percent variance explained is displayed on each axis.  This report provides the following beta diversity metrics:\n",
    "- __Bray-Curtis dissimilarity:__ Fraction of overabundant counts; creates a matrix of the differences in microbial abundances between two samples (0 indicates that the samples share the same species at the same abundances, 1 indicates that both samples have completely different species and abundances)\n",
    "- __Jaccard similarity index:__ Fraction of unique features, regardless of abundance\n",
    "- __Unweighted UniFrac:__ Measures the phylogenetic distance between sets of taxa in a phylogenetic tree as the fraction of unique branch length\n",
    "- __Weighted UniFrac:__ Same as above, but takes into account the relative abundance of each of the taxa\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!unzip -q -d diversity_core_metrics/rpt_bray-curtis_dist diversity_core_metrics/bray-curtis_dist.qza\n",
    "!unzip -q -d diversity_core_metrics/rpt_weighted_dist diversity_core_metrics/weighted_dist.qza\n",
    "!unzip -q -d diversity_core_metrics/rpt_unweighted_dist diversity_core_metrics/unweighted_dist.qza\n",
    "!unzip -q -d diversity_core_metrics/rpt_jaccard_dist diversity_core_metrics/jaccard_dist.qza"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "m['Sequencer'] = (manifest['run-id'].str.split('_',n=2,expand=True))[1]\n",
    "if 'sourcepcrplate' in manifest.columns:\n",
    "    m['PCR_plate'] = (manifest['sourcepcrplate'].str.split('_',n=1,expand=True))[0]\n",
    "m['run-id'] = (manifest['run-id'].str.split('-',expand=True)[1])\n",
    "m.fillna('na', inplace=True)\n",
    "# should probably save this file, or even better, include in original manifest prior to analysis...."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import warnings\n",
    "warnings.filterwarnings(\"ignore\", message=\"The result contains negative eigenvalues. Please compare their magnitude with the magnitude of some of the largest positive eigenvalues\")\n",
    "# NOTE: without this filter, pcoa plotting may generate runtime warning messages like the following:\n",
    "    # /Users/ballewbj/anaconda3/lib/python3.7/site-packages/skbio/stats/ordination/_principal_coordinate_analysis.py:152: \n",
    "    # RuntimeWarning: The result contains negative eigenvalues. Please compare their magnitude with the magnitude of some \n",
    "    # of the largest positive eigenvalues. If the negative ones are smaller, it's probably safe to ignore them, but if \n",
    "    # they are large in magnitude, the results won't be useful. See the Notes section for more details. The smallest \n",
    "    # eigenvalue is -0.41588455816214936 and the largest is 9.807175722836307.\n",
    "    # RuntimeWarning\n",
    "# This warning is explained in detail here: https://github.com/biocore/scikit-bio/issues/1410"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_pcoas(metric):\n",
    "    mpl.rcParams['figure.dpi'] = 100\n",
    "    mpl.rcParams['figure.figsize'] = 9, 6\n",
    "    df = pd.read_csv(glob.glob('diversity_core_metrics/rpt_' + metric + '_dist/*/data/distance-matrix.tsv')[0],sep='\\t',index_col=0)\n",
    "    sample_ids = df.index.values\n",
    "    dist = df.to_numpy()\n",
    "    dm = DistanceMatrix(dist, sample_ids)\n",
    "    pc = pcoa(dm)\n",
    "    var1 = str(round(pc.proportion_explained[0]*100, 2))\n",
    "    var2 = str(round(pc.proportion_explained[1]*100, 2))\n",
    "    var3 = str(round(pc.proportion_explained[2]*100, 2))\n",
    "    for i in m.columns:\n",
    "        ax = pc.plot(m, i, cmap='Accent', axis_labels=('PC1, '+var1+'%', 'PC2, '+var2+'%', 'PC3, '+var3+'%'), title= metric + \" PCoA colored by \" + i)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"6.1&nbsp;&nbsp;Bray-Curtis\">6.1&nbsp;&nbsp;Bray-Curtis</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "plot_pcoas('bray-curtis')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"6.2&nbsp;&nbsp;Jaccard\">6.2&nbsp;&nbsp;Jaccard</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "plot_pcoas('jaccard')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"6.3&nbsp;&nbsp;Weighted-UniFrac\">6.3&nbsp;&nbsp;Weighted UniFrac</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "plot_pcoas('weighted')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h3 id=\"6.4&nbsp;&nbsp;Unweighted-UniFrac\">6.4&nbsp;&nbsp;Unweighted UniFrac</h3>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "plot_pcoas('unweighted')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%rm -r */rpt_* */*/rpt_*"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "hide_input": false,
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.3"
  },
  "toc": {
   "base_numbering": 1,
   "nav_menu": {},
   "number_sections": false,
   "sideBar": true,
   "skip_h1_title": true,
   "title_cell": "Table of Contents",
   "title_sidebar": "Contents",
   "toc_cell": false,
   "toc_position": {
    "height": "calc(100% - 180px)",
    "left": "10px",
    "top": "150px",
    "width": "299px"
   },
   "toc_section_display": true,
   "toc_window_display": true
  },
  "varInspector": {
   "cols": {
    "lenName": 16,
    "lenType": 16,
    "lenVar": 40
   },
   "kernels_config": {
    "python": {
     "delete_cmd_postfix": "",
     "delete_cmd_prefix": "del ",
     "library": "var_list.py",
     "varRefreshCmd": "print(var_dic_list())"
    },
    "r": {
     "delete_cmd_postfix": ") ",
     "delete_cmd_prefix": "rm(",
     "library": "var_list.r",
     "varRefreshCmd": "cat(var_dic_list()) "
    }
   },
   "position": {
    "height": "300px",
    "left": "1583px",
    "right": "20px",
    "top": "120px",
    "width": "317px"
   },
   "types_to_exclude": [
    "module",
    "function",
    "builtin_function_or_method",
    "instance",
    "_Feature"
   ],
   "window_display": false
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
