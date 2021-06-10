#!/bin/bash
set -e # -xe

# =============================================================================
# @Brief:   This file is used to create the list of train and test files for
#           training/testing procedures. They map each image to its label file.
# @Outputs: trainval.txt, test.txt and test_name_size.txt .
# @Note:    1) The outputs can be shared by all classes;
# =============================================================================

root_dir=$HOME/data/VOCdevkit/
tool_dir=$HOME/desktop/caffe/build/tools
sub_dir=ImageSets/Main
bash_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for dataset in trainval test; do
  dst_file=$bash_dir/$dataset.txt
  if [ -f $dst_file ]; then
    rm -f $dst_file
  fi
  for name in VOC2007 VOC2012; do
    if [[ $dataset == "test" && $name == "VOC2012" ]]; then
      ## VOC2012 doesn't have test.txt file
      continue
    fi
    echo "Create list for $name $dataset..."
    dataset_file=$root_dir/$name/$sub_dir/$dataset.txt

    img_file=$bash_dir/$dataset"_img.txt"
    cp $dataset_file $img_file
    sed -i "s/^/$name\/JPEGImages\//g" $img_file
    sed -i "s/$/.jpg/g" $img_file

    label_file=$bash_dir/$dataset"_label.txt"
    cp $dataset_file $label_file
    sed -i "s/^/$name\/Annotations\//g" $label_file
    sed -i "s/$/.xml/g" $label_file

    paste -d' ' $img_file $label_file >> $dst_file

    rm -f $label_file
    rm -f $img_file
  done

  # Generate image name and size infomation.
  if [ $dataset == "test" ]; then
    echo "Generate image name and size infomation ..."
    if [ -f $tool_dir/get_image_size ]; then
       $tool_dir/get_image_size $root_dir $dst_file $bash_dir/$dataset"_name_size.txt"
    else
      ## get image size by identify
      rm -rf $bash_dir/$dataset"_name_size.txt"
      while read line; do
        line=${line%% *}
        size=`identify ${root_dir}/${line} | cut -d ' ' -f 3 | sed -e "s/x/ /" | sed -r 's/([^ ]+) (.*)/\2 \1/'`
        name=$(basename ${line})
        name=${name%%.*}
        echo ${name}" "${size} >> $bash_dir/$dataset"_name_size.txt"
      done < $dst_file
    fi
  fi

  # Shuffle trainval file.
  if [ $dataset == "trainval" ]; then
    echo "Shuffle trainval file ..."
    rand_file=$dst_file.random
    if [ $(which perl) ]; then
      cat $dst_file | perl -MList::Util=shuffle -e 'print shuffle(<STDIN>);' > $rand_file
      mv $rand_file $dst_file
    else
      ## shuffle by awk
      cp $dst_file $rand_file
      awk 'BEGIN{srand()}{b[rand()NR]=$0}END{for(x in b)print b[x]}' $rand_file > $dst_file
      rm -f $rand_file
    fi
  fi
done
