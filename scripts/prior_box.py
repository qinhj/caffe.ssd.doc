
## Note: The feature map size is totally depend on the input image size of the model.
## e.g. with input image size: 300x300, the featur maps of SSD are:
feature_map = [
    (38, 38),   # P3/8
    (19, 19),   # P4/16
    (10, 10),   # P5/32
    (5, 5),     # P6/64
    (3, 3),     # P7/128
    (1, 1),     # P8/256
]

## @brief:  scale(< 1.0) for each feature map
## @param:  k[in] feature map index(k = 0, 1, 2, ..., m-1 for ssd)
## @return: scale(k)
## @note:   The scale is totally depend on the training dataset and model.
##          It has nothing to do with the test/val image resolution.
def s_size(k=0):
    smin = 0.2  # voc 2007 dataset
    smax = 0.9  # voc 2007 dataset
    m = 6       # total feature map number
    ssize = smin + (smax - smin) / (m - 1) * k
    return ssize

## @brief:  calculate default box's size according to perdefined ARs(Aspect Ratio) and feature map's scale
## @param:  ssize[in] scale(k)
## @param:  k[in] feature map index(k = 1, 2, ..., 6 for ssd)
## @return: (width, height) with fixed length 6
## @note:   both output width and height are < 1.0, and they are totally depend on the scale and ARs
def w_h(ssize, k):
    import math
    width = []
    height = []
    aspect_ratio = [1, 2, 3, 1/2, 1/3]
    ssize2 = s_size(k + 1)
    ssize2 = math.sqrt(ssize2 * ssize)
    ## additional default box with scale sqrt(scale(k)*scale(k+1))
    width.append(ssize2 * math.sqrt(aspect_ratio[0]))
    height.append(ssize2 / math.sqrt(aspect_ratio[0]))
    for i in range(len(aspect_ratio)):
        width.append(ssize * math.sqrt(aspect_ratio[i]))
        height.append(ssize / math.sqrt(aspect_ratio[i]))
    return width, height

## @brief:  create default box for the kth feature map
## @param:  fm_idx[in] feature map index
## @return: prior box list (totally depend on the scale and ARs)
def default_box(fm_idx=0):
    widths, heights =  w_h(s_size(fm_idx), fm_idx)
    bboxes = []
    ## create default box for point(i, j) in the feature map
    for i in range(feature_map[fm_idx][0]):
        for j in range(feature_map[fm_idx][1]):
            center_x = (i + 0.5) / feature_map[fm_idx][0]
            center_y = (j + 0.5) / feature_map[fm_idx][1]
            bboxij = []
            for num in range(len(widths)):
                box = []
                #xmin,ymin,xmax,ymax
                box.append(max(0, center_x - widths[num] / 2))
                box.append(max(0, center_y - heights[num] / 2))
                box.append(min(1, center_x + widths[num] / 2))
                box.append(min(1, center_y + heights[num] / 2))
                bboxij.append(box)
            bboxes.append(bboxij)
    return bboxes

def draw_box(path, bboxes):
    import cv2
    img = cv2.imread(path)
    #img = cv2.resize(img, (500, 500), interpolation=cv2.INTER_AREA)
    h, w = img.shape[0:2]
    for num in range(6):
        x1 = int(bboxes[num][0] * w)
        y1 = int(bboxes[num][1] * h)
        x2 = int(bboxes[num][2] * w)
        y2 = int(bboxes[num][3] * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2) 
    cv2.imshow('bbox', img)
    cv2.waitKey(0)

def main():
    ## show ssd scale(k)
    for k in range(6):
        print("scale(%d): %s" % (k, s_size(k)))
    ## test feature map shape 10 with index 3
    bboxes = default_box(fm_idx=1) # for idx 2, 45 is a good test case
    draw_box('test.jpg', bboxes[183]) # len(bboxes)//2

if __name__ == '__main__':
    main() 
