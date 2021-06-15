#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Brief:   extract target classes from voc dataset for classification or object detection
# @Author:  qinhj@lsec.cc.ac.cn
# @Usage:   python voc_extract.py --dataset $HOME/data --classes cat,dog,person
# @Todo:    1) support remove 'difficult' or 'truncated' annotations;

import argparse
import os
import xml.etree.ElementTree as ET


def extract_annotation(file_xml, file_out, classes, truncated=False, difficult=False):
    '''
    Args:
        classes     extract class list
        truncated   keep truncated or not
        difficult   keep difficult or not
    '''
    fin = open(file_xml)
    tree = ET.parse(fin)
    fin.close()
    root = tree.getroot()
    for obj in root.findall('object'):
        if obj.find('name').text in classes:
            if (int(obj.find('difficult').text) and not difficult) or \
                (int(obj.find('truncated').text) and not truncated):
                ## ignore by truncated or difficult
                root.remove(obj)
        else:
            ## ignore by name as label
            root.remove(obj)
    #[print(obj) for obj in root.iter('object')]
    if root.find('object'):
        tree.write(file_out)
        return True
    return False


## construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", type=str, default="./", help="path of VOCdevkit")
ap.add_argument("-y", "--year", type=str, default="2007,2012", help="year of VOC datasets")
ap.add_argument("-c", "--classes", type=str, default="person", help="extract classes(e.g. cat,dog)")
ap.add_argument("-o", "--output", type=str, default="output", help="output dir")
args = vars(ap.parse_args())
#print("args: %s" % args)

## VOC datasets: year
years = args["year"].split(",")
lists = []
for y in years:
    lists.extend([(y, 'train'), (y, 'val'), (y, 'trainval')])
    if "2012" != y:
        lists.append((y, 'test'))
print("VOC dataset lists:", lists)

import sys
import shutil

## create output dir
output = os.path.join(args["output"], "VOCdevkit")
if os.path.exists(output):
    shutil.rmtree(output)
os.makedirs(output)

for (y, t) in lists:
    voc_path = os.path.join("VOCdevkit", "VOC" + y)
    voc_path_xml = os.path.join(voc_path, "Annotations")
    voc_path_set = os.path.join(voc_path, "ImageSets")
    voc_path_img = os.path.join(voc_path, "JPEGImages")
    voc_path_set_main = os.path.join(voc_path_set, "Main")
    ## check dirs
    for d in [voc_path, voc_path_xml, voc_path_set, voc_path_set_main]:
        _d_fullpath = os.path.join(args["output"], d)
        if not os.path.exists(_d_fullpath): os.makedirs(_d_fullpath)
    if not os.path.exists(os.path.join(args["output"], voc_path_img)):
        os.symlink(os.path.join(args["dataset"], voc_path_img), os.path.join(args["output"], voc_path_img))
    ## copy target *.txt files
    voc_path_list = [os.path.join(voc_path_set_main, t + ".txt")]
    #[voc_path_list.append(os.path.join(voc_path_set_main, f + "_" + t + ".txt")) for f in args["classes"].split(",")]
    #print(voc_path_list)
    try:
        for f in voc_path_list:
            shutil.copy(os.path.join(args["dataset"], f), os.path.join(args["output"], f))
    except IOError as e:
        print("Unable to copy file. %s" % e)
    except:
        print("Unexpected error:", sys.exc_info())
    ## go through all images and xml files
    images = open(os.path.join(args["dataset"], voc_path_list[0])).readlines()
    fout = open(os.path.join(args["output"], voc_path_list[0]), "w")
    for img in images:
        img = img.strip().split()[0]
        src_xml = os.path.join(args["dataset"], voc_path_xml, img + ".xml")
        dst_xml = os.path.join(args["output"], voc_path_xml, img + ".xml")
        if not os.path.exists(dst_xml):
            b = extract_annotation(src_xml, dst_xml, args["classes"].split(","), True, True)
            if b: fout.write(img + "\n")
        elif "trainval" == t:
            fout.write(img + "\n")
    fout.close()
