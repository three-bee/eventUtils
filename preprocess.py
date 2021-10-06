"""
Preprocessing of frames. Consists of resizing, downsampling and cropping, all in batches.
"""
import os
import argparse
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('--imgpath', type=str, help='Path of high framerate images')
parser.add_argument('--flowpath', type=str, help='Path of flo files of highrate images')
parser.add_argument('--rate', type=int, help='Rate of downsampling')
parser.add_argument('--resizeratio', type=float, help='Resize ratio. w & h -> w/ratio & h/ratio')
args = parser.parse_args()

def batch_reduce_rate(images_path, rate):
    images_list = sorted(next(os.walk(images_path))[2])
    dst = images_path[0:-1] + '_lowrate'

    try:
        os.makedirs(dst)
    except OSError:
        pass

    total_images = len(images_list)
    for i in range(0,total_images):
        try:
            src = images_path + images_list[i*rate]
        except IndexError:
            break
        command = 'cp ' + src + ' ' + dst
        os.popen(command)
    
    print('Done downsampling: ' + dst)
    return dst+'/'
    
def batch_crop_1to1(images_path):
    images_list = sorted(next(os.walk(images_path))[2])
    (y,x,_) = cv2.imread(images_path + images_list[0]).shape
    crop_size = y if y<x else x

    dst = images_path + 'cropped'
    try:
        os.makedirs(dst)
    except OSError:
        pass
    
    for idx,image in enumerate(images_list):
        src = images_path + image
        offset = int((x-crop_size)/2) if x>crop_size else int((y-crop_size)/2)
        cv_img = cv2.imread(src)[:, offset : -offset]
        cv_img = cv2.resize(cv_img, (crop_size, crop_size))
        cv2.imwrite(dst + '/cropped%03d.png'%idx, cv_img)
    
    print('Done cropping: ' + dst)
    print(cv_img.shape)
    return dst+'/'

def batch_resize(images_path,ratio):
    images_list = sorted(next(os.walk(images_path))[2])
    (y,x,_) = cv2.imread(images_path + images_list[0]).shape

    dst = images_path + 'resized'
    try:
        os.makedirs(dst)
    except OSError:
        pass

    for idx, image in enumerate(images_list):
        src = images_path + image
        cv_img = cv2.imread(src)
        (r_x,r_y) = (int(x/ratio),int(y/ratio))
        resized = cv2.resize(cv_img, (r_x,r_y))
        cv2.imwrite(dst + '/resized%03d.png'%idx, resized)
    
    print('Done resizing: ' + dst)
    return dst+'/'

def main():
    #TODO: bad practice for indexing, fix other solution
    lowratepath = args.imgpath[:-1] + '_lowrate/'

    batch_reduce_rate(args.imgpath, args.rate)
    batch_reduce_rate(args.flowpath, args.rate)

    resized_highrate_path = batch_resize(args.imgpath, args.resizeratio)
    resized_lowrate_path = batch_resize(lowratepath, args.resizeratio)

    batch_crop_1to1(resized_highrate_path)
    batch_crop_1to1(resized_lowrate_path)

if __name__=='__main__':
    main()