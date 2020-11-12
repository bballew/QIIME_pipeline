#!/bin/bash

# CGR QIIME2 pipeline for microbiome analysis.
#
# AUTHORS:
#     Y. Wan
#     S. Sevilla Chill
#     W. Zhou
#     B. Ballew
#
# TO RUN:
#     Have conda and mamba in $PATH
#     Copy config.yaml to local dir and edit as needed
#     Edit below and then run: `bash run_pipeline.sh`

set -euo pipefail

. /etc/profile.d/modules.sh; module load sge
unset module

cmd="qsub -q seq-calling.q -V -j y -S /bin/sh -cwd workflow/scripts/Q2_wrapper.sh config/config.yaml"
echo "Command run: $cmd"
eval "$cmd"
