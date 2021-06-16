#!/bin/bash
set -e # -xe

# =============================================================================
# @Brief:   This file is used to create the "db"(e.g. lmdb) file for train and
#           test data, along with example softlink dir.
# @Outputs: "db" dir and example dir
# =============================================================================

caffe_dir=$HOME/desktop/caffe
cur_dir=$(cd $( dirname ${BASH_SOURCE[0]} ) && pwd )

#cd $caffe_dir

redo=1

data_dir="$HOME/data/VOCdevkit"
#dataset_name="VOC0712"

mapfile="$cur_dir/labelmap_voc.prototxt"
anno_type="detection"
db="lmdb"
min_dim=0
max_dim=0
width=0
height=0

extra_cmd="--encode-type=jpg --encoded"
if [ $redo ]; then
  extra_cmd="$extra_cmd --redo"
fi

## remove exist softlink
[ -d examples/$dataset_name ] && rm -rf examples/$dataset_name

for subset in test trainval; do
# =====================================================================
# usage: create_annoset.py [-h] [--redo] [--anno-type ANNO_TYPE]
#                          [--label-type LABEL_TYPE] [--backend BACKEND]
#                          [--check-size] [--encode-type ENCODE_TYPE]
#                          [--encoded] [--gray]
#                          [--label-map-file LABEL_MAP_FILE] [--min-dim MIN_DIM]
#                          [--max-dim MAX_DIM] [--resize-height RESIZE_HEIGHT]
#                          [--resize-width RESIZE_WIDTH] [--shuffle]
#                          [--check-label]
#                          root listfile outdir exampledir
# where
#   root          as dataset root dir
#   listfile      as trainval.txt/test.txt
#   outdir        as output "db" file path
#   exampledir    as output dir with softlink
# =====================================================================
  python $caffe_dir/scripts/create_annoset.py \
    --anno-type=$anno_type \
    --label-map-file=$mapfile \
    --min-dim=$min_dim --max-dim=$max_dim \
    --resize-width=$width --resize-height=$height \
    --check-label $extra_cmd \
    $data_dir \
    $cur_dir/$subset.txt \
    $cur_dir/$db/$subset"_"$db \
    $cur_dir/examples
done
