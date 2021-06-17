#!/bin/bash
set -e # -xe

# =============================================================================
# @Brief:   This file is used to create the "db"(e.g. lmdb) file for train and
#           test data, along with example softlink dir.
# @Outputs: "db" dir and example dir
# =============================================================================

caffe_dir=$HOME/desktop/caffe
cur_dir=$(cd $( dirname ${BASH_SOURCE[0]} ) && pwd )

data_dir="$HOME/data/VOCdevkit"
out_dir_lmdb=$cur_dir/VOC0712 #$data_dir/VOC0712
out_dir_link=$cur_dir

redo=1
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

for subset in test trainval; do
  ## remove exist softlink
  rm -rf $out_dir_link/$subset"_"$db

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
    $out_dir_lmdb/$subset"_"$db \
    $out_dir_link
done
