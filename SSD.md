## Quick Start ##
```
* Plz review caffe/Readme.md first.

## clone source code
$ git clone https://github.com/weiliu89/caffe.git
$ cd caffe
$ git checkout ssd

## env var settings
$ export CAFFE_ROOT=$HOME/desktop/caffe/
$ export PYTHONPATH=$CAFFE_ROOT/python:$PYTHONPATH

## quick make && test
$ cd $CAFFE_ROOT
$ cp Makefile.config.example Makefile.config
$ vim Makefile.config # e.g. caffe/Makefile.config.cpu.miniconda3
$ make -j`nproc`
$ make py
$ make test -j`nproc`
$ make runtest -j`nproc` # optional
```

## Quick Preparation ##
```
## download fully convolutional reduced (atrous) VGGNet.
$ wget https://owncloud.gwdg.de/index.php/s/SjXmX0Uqh1zaYgI/download

## download dataset
$ cd $HOME/data
$ wget http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar
$ wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar
$ wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest_06-Nov-2007.tar
## Extract the data.
$ tar -xvf VOCtrainval_11-May-2012.tar
$ tar -xvf VOCtrainval_06-Nov-2007.tar
$ tar -xvf VOCtest_06-Nov-2007.tar

## create the LMDB file
$ cd $CAFFE_ROOT
## Create the trainval.txt, test.txt, and test_name_size.txt in data/VOC0712/
$ ./data/VOC0712/create_list.sh
## You can modify the parameters in create_data.sh if needed.
## It will create lmdb files for trainval and test with encoded original image:
##   - $HOME/data/VOCdevkit/VOC0712/lmdb/VOC0712_trainval_lmdb
##   - $HOME/data/VOCdevkit/VOC0712/lmdb/VOC0712_test_lmdb
## and make soft links at examples/VOC0712/
$ ./data/VOC0712/create_data.sh
```

## Train/Eval/Detect ##
```
## Train
## It will create model definition files and save snapshot models in:
##   - $CAFFE_ROOT/models/VGGNet/VOC0712/SSD_300x300/
## and job file, log file, and the python script in:
##   - $CAFFE_ROOT/jobs/VGGNet/VOC0712/SSD_300x300/
## and save temporary evaluation results in:
##   - $HOME/data/VOCdevkit/results/VOC2007/SSD_300x300/
## It should reach 77.* mAP at 120k iterations.
$ python examples/ssd/ssd_pascal.py

## Eval
## If you would like to test a model you trained, you can do:
$ python examples/ssd/score_ssd_pascal.py

## Detect (with CPU)
$ python examples/ssd/ssd_detect.py --gpu_id -1
```

## Quick FAQ ##
```
1. Data layer prefetch queue empty
https://github.com/weiliu89/caffe/issues/863
```

## Layer List ##
```
===================================================================================
No. VGG16       Output Shape  Name  |   Output Shape    SSD     No. Name  AnchorBox
===================================================================================
 0  --------    224x224x3           |   300x300x3
-----------------------------------------------------------------------------------
 1  conv3-64    224x224x64  conv1_1 |   300x300x64
 2  conv3-64    224x224x64  conv1_2 |   300x300x64
    maxpool/2   112x112x64          |   150x150x64
 3  conv3-128   112x112x128 conv2_1 |   150x150x128
 4  conv3-128   112x112x128 conv2_2 |   150x150x128
    maxpool/2   56x56x128           |   75x75x128
 5  conv3-256   56x56x256   conv3_1 |   75x75x256
 6  conv3-256   56x56x256   conv3_2 |   75x75x256
 7  conv3-256   56x56x256   conv3_3 |   75x75x256
    maxpool/2   28x28x256           |   38x38x256
 8  conv3-512   28x28x512   conv4_1 |   38x38x512
 9  conv3-512   28x28x512   conv4_2 |   38x38x512
10  conv3-512   28x28x512   conv4_3 |   38x38x512   (4) -> 5776=38*38*4 P3/8
    maxpool/2   14x14x512           |   19x19x512
11  conv3-512   14x14x512   conv5_1 |   19x19x512
12  conv3-512   14x14x512   conv5_2 |   19x19x512
13  conv3-512   14x14x512   conv5_3 |   19x19x512
    maxpool/2   7x7x512             |   ---------
-----------------------------------------------------------------------------------
14  FC-4096     1x1x4096    (FC6)   |   19x19x1024  conv3-1024   14 Conv6
15  FC-4096     1x1x4096    (FC7)   |   19x19x1024  conv1-1024   15 Conv7    (6) -> 2166=19*19*6 P4/16
16  FC-1000     1x1x1000            |   19x19x256   conv1-256    16 Conv8_1
    softmax                         |   10x10x512   conv3-512/s2 17 Conv8_2  (6) -> 600=10*10*6  P5/32
                                    |   10x10x128   conv1-128    18 Conv9_1
                                    |   5x5x256     conv3-256/s2 19 Conv9_2  (6) -> 150=5*5*6    P6/64
                                    |   5x5x128     conv1-128    20 Conv10_1
                                    |   3x3x256     conv3-256/s1 21 Conv10_2 (4) -> 36=3*3*4 (no padding)
                                    |   3x3x128     conv1-128    22 Conv11_1
                                    |   1x1x256     conv3-256/s1 23 Conv11_2 (4) -> 4=1*1*4
-----------------------------------------------------------------------------------
                                        total prior box: 8732 = 5776 + 2166 + 600 + 150 + 36 + 4
```

## Prior Box ##
```
1. D_min x D_min, with (x_offset, y_offset);
2. D_min/sqrt(AR_i) x D_min*sqrt(AR_i) and D_min*sqrt(AR_i) x D_min/sqrt(AR_i), with (x_offset, y_offset);
3. D_max x D_max, with (x_offset, y_offset);

For image size 300x300, scale = BoxSiz/ImageSiz => scale_min = 0.2, scale_max = 0.9,
Dmin = 60, D_max = 270. scale_k = scale_min + (scale_max - scale_min)/(m - 1)*(k - 1), k = 1, ..., m.

* more details in examples/ssd/ssd_pascal.py:
# parameters for generating priors.
# minimum dimension of input image
min_dim = 300
# conv4_3 ==> 38 x 38
# fc7 ==> 19 x 19
# conv6_2 ==> 10 x 10
# conv7_2 ==> 5 x 5
# conv8_2 ==> 3 x 3
# conv9_2 ==> 1 x 1
mbox_source_layers = ['conv4_3', 'fc7', 'conv6_2', 'conv7_2', 'conv8_2', 'conv9_2']
min_ratio = 20
max_ratio = 90
step = int(math.floor((max_ratio - min_ratio) / (len(mbox_source_layers) - 2))) <-- here: step=17=70//4
min_sizes = []
max_sizes = []
for ratio in xrange(min_ratio, max_ratio + 1, step):    <-- note: use range for python3,
  min_sizes.append(min_dim * ratio / 100.)              <-- here: [20, 37, 54, 71,  88] * 3
  max_sizes.append(min_dim * (ratio + step) / 100.)     <-- here: [37, 54, 71, 88, 105] * 3
min_sizes = [min_dim * 10 / 100.] + min_sizes   <-- here: [30.0, 60.0, 111.0, 162.0, 213.0, 264.0]
max_sizes = [min_dim * 20 / 100.] + max_sizes   <-- here: [60.0, 111.0, 162.0, 213.0, 264.0, 315.0]
steps = [8, 16, 32, 64, 100, 300]                       <-- here: the step_h && step_w
aspect_ratios = [[2], [2, 3], [2, 3], [2, 3], [2], [2]]

* more details in src/caffe/layers/prior_box_layer.cpp:
  for (int h = 0; h < layer_height; ++h) {
    for (int w = 0; w < layer_width; ++w) {
      float center_x = (w + offset_) * step_w;  <-- here!
      float center_y = (h + offset_) * step_h;  <-- here!
      float box_width, box_height;
      for (int s = 0; s < min_sizes_.size(); ++s) {     <-- here: why ?? it seems that min_sizes_.size()=1, same as max
        int min_size_ = min_sizes_[s];          <-- here!
        // first prior: aspect_ratio = 1, size = min_size
        box_width = box_height = min_size_;     <-- here!
        // xmin
        top_data[idx++] = (center_x - box_width / 2.) / img_width;
        ...
  // clip the prior's coordidate such that it is within [0, 1]  <-- here: !!
  if (clip_) {
    for (int d = 0; d < dim; ++d) {
      top_data[d] = std::min<Dtype>(std::max<Dtype>(top_data[d], 0.), 1.);
    }
  }

* So, from the above source code, we can see that the anchor boxes are actually fixed(same as yolov3, in my opinion).
=================================================================================================================
feature map | feature map size | min_size(sk,sk) | max_size(sk+1,sk+1) | aspect_ratio | step | offset | variance
------------+------------------+-----------------+---------------------+--------------+------+--------+----------
conv4_3     |       38��38      |        30       |          60         |      1,2     |   8  |        |
fc6         |       19��19      |        60       |         111         |     1,2,3    |  16  |        |  0.1
conv6_2     |       10��10      |       111       |         162         |     1,2,3    |  32  |  0.5   |  0.1
conv7_2     |       5��5        |       162       |         213         |     1,2,3    |  64  |        |  0.2
conv8_2     |       3��3        |       213       |         264         |      1,2     | 100  |        |  0.2
conv9_2     |       1��1        |       264       |         315         |      1,2     | 300  |        |
=================================================================================================================
```

## Source Code Info ##
```
cafe/examples/ssd/ssd_pascal.py
cafe/python/caffe/model_libs.py
cafe/src/caffe/layers/prior_box_layer.cpp
cafe/src/caffe/test/test_prior_box_layer.cpp
```