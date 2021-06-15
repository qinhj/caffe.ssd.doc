#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Brief:   ssd(caffe) lmdb visual
# @Author:  qinhj@lsec.cc.ac.cn
# @Usage:   python lmdb_visual.py
# @Reference: https://blog.csdn.net/Touch_Dream/article/details/80598901

import argparse
import os
import lmdb
import caffe
import numpy as np
import cv2


## construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--lmdb", type=str, default="trainval_lmdb", help="path of lmdb")
args = parser.parse_args()
#print("args: %s" % args)

env = lmdb.open(args.lmdb, readonly=True)
txn = env.begin()
cur = txn.cursor()
## ssd(caffe) data struct
annotated_datum = caffe.proto.caffe_pb2.AnnotatedDatum()

for key, value in cur:
    name = os.path.basename(key.decode())
    
    ## deserialize ssd(caffe) annotated datum object
    annotated_datum.ParseFromString(value)
    #print("type:", annotated_datum.type)
    datum = annotated_datum.datum
    print("label:   ", datum.label)
    print("channels:", datum.channels)
    print("height:  ", datum.height)
    print("width:   ", datum.width)
    
    groups = annotated_datum.annotation_group
    for group in groups:
        xmin = group.annotation[0].bbox.xmin * datum.width
        ymin = group.annotation[0].bbox.ymin * datum.height
        xmax = group.annotation[0].bbox.xmax * datum.width
        ymax = group.annotation[0].bbox.ymax * datum.height
        print("label:", group.group_label)
        print("bbox: ", xmin, ymin, xmax, ymax)

    ## string to numpy
    image_x = np.fromstring(datum.data, dtype=np.uint8)
    image = cv2.imdecode(image_x, -1)
    cv2.imshow(name, image)
    if (27 == cv2.waitKey(0)): break
    #if ord('q') == cv2.waitKey(1) & 0xFF: break

#cv2.destoyAllWindows()
env.close()
