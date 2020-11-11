#!/bin/sh

# CGR QIIME2 pipeline for microbiome analysis.
#
# AUTHORS:
#     Y. Wan
#     S. Sevilla Chill
#     W. Zhou
#     B. Ballew
#
# TO RUN:
#     Have conda and snakemake in $PATH
#     Copy config.yaml to local dir and edit as needed
#     Submit this script to a cluster or run locally
#     See run_pipeline.sh for example

# POSIX compliance notes:
    # -o pipefail
    # possibly `source activate conda-env`

set -euo pipefail

unset module

usage="Usage: $0 /path/to/config.yaml"

# custom exit function
die() {
    printf "ERROR: %s\n" "$*" 1>&2
    exit 1
}

config_file=""
if [ $# -eq 0 ]; then
    die "Please specify config file with full path.
$usage"
else
    config_file=$1
fi

if [ ! -f "$config_file" ]; then
    die "Config file not found.
$usage"
fi

# note that this will only work for simple, single-level yaml
# and requires a whitespace between the key and value pair in the config
# (except for the cluster command, which requires single or double quotes)
temp_dir=$(awk '($0~/^temp_dir/){print $2}' "$config_file" | sed "s/['\"]//g")
num_jobs=$(awk '($0~/^num_jobs/){print $2}' "$config_file" | sed "s/['\"]//g")
latency=$(awk '($0~/^latency/){print $2}' "$config_file" | sed "s/['\"]//g")
cluster_line=$(awk '($0~/^cluster_mode/){print $0}' "$config_file" | sed "s/\"/'/g")
    # allows single or double quoting of the qsub command in the config file
cluster_mode='"'$(echo "$cluster_line" | awk -F\' '($0~/^cluster_mode/){print $2}')'"'

# emit pipeline version
echo ""
echo "CGR QIIME pipeline version:"
git describe 2> /dev/null || die "Unable to determine pipeline version information."
echo ""

# export temp directory (otherwise defaults to /tmp)
# https://forum.qiime2.org/t/tmp-directory-for-qiime-dada2-denoise-paired/6384
if [ ! -d "$temp_dir" ]; then
    mkdir -p "$temp_dir" || die "mkdir -p ${temp_dir} failed."
fi
export TMPDIR="$temp_dir"

# check config file for errors (TODO)
# perl ${execDir}/scripts/check_config.pl $config_file

if [ ! -d "results/logs/" ]; then
    mkdir -p "results/logs/" || die "mkdir -p results/logs/ failed."
fi

DATE=$(date +"%Y%m%d%H%M")

cmd=""
if [ "$cluster_mode" = '"'"local"'"' ]; then
    cmd="conf=$config_file snakemake -p --rerun-incomplete --use-conda --conda-frontend mamba &> results/logs/Q2_${DATE}.out"
elif [ "$cluster_mode" = '"'"unlock"'"' ]; then
    cmd="conf=$config_file snakemake -p --unlock"  # convenience unlock
elif [ "$cluster_mode" = '"'"dryrun"'"' ]; then
    cmd="conf=$config_file snakemake -n -p"  # convenience dry run
else
    cmd="conf=$config_file snakemake -p --rerun-incomplete --use-conda --conda-frontend mamba --cluster ${cluster_mode} --jobs $num_jobs --latency-wait ${latency} &> results/logs/Q2_${DATE}.out"
fi

echo "Command run: $cmd"
eval "$cmd"
