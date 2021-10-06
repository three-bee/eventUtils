'''
Includes some metrics related to optical flow calculations.
AEE (EPE) : average endpoint error

AEE calculations can be masked with events, if desired.
'''
import os
import argparse
import numpy as np
import flowpy
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('--gtflowpath', type=str, help='Path of gt flow')
parser.add_argument('--predflowpath', type=str, help='Path of pred flow')
parser.add_argument('--ratio', type=float, help='Resize ratio for ground truth flow.')
parser.add_argument('--crop', type=bool, default=True, help='True if flow files in gtflowpath need to be cropped in 1:1 (from center).')
parser.add_argument('--maskenabled', type=str, default='True', help='Mask enable flag.')
parser.add_argument('--maskpath', type=str, default='not a meaningful path', help='Path of event masks.')
args = parser.parse_args()

def avg_endpoint_error(gt_flow, pred_flow):
    EE = np.linalg.norm(gt_flow - pred_flow, axis=-1)
    AEE = np.mean(EE)
    return AEE

def avg_endpoint_error_masked(gt_flow, pred_flow, mask):
    EE = np.linalg.norm(gt_flow - pred_flow, axis=-1)
    EE = np.logical_and(EE, mask)
    AEE = np.mean(EE)
    return AEE

gtflow_path_list = sorted(next(os.walk(args.gtflowpath))[2]) #Does not include subfolders. All items in the directory must be flo files.
predflow_path_list = sorted(next(os.walk(args.predflowpath))[2])
mask_path_list = sorted(next(os.walk(args.maskpath))[2])
total_number_flow = len(gtflow_path_list)

y = flowpy.flow_read(args.gtflowpath + gtflow_path_list[0]).shape[0]
x = flowpy.flow_read(args.gtflowpath + gtflow_path_list[0]).shape[1]

AEE_sum = 0

for i in range(0,total_number_flow-1):
    #Process ground truth flow (resize, cut from center)
    gt_flow = flowpy.flow_read(args.gtflowpath + gtflow_path_list[i])

    f_y,f_x,_ = gt_flow.shape
    ratio = args.ratio
    crop_size = int(f_y/ratio) if y<=x else int(f_x/ratio)

    if args.crop:
        #First resize
        (x,y) = (int(f_x/ratio), int(f_y/ratio))
        u = cv2.resize(gt_flow[...,0],(x,y))
        v = cv2.resize(gt_flow[...,1],(x,y))
        #Then crop 1:1 image flow from the middle
        offset = int((x-crop_size)/2) if x>crop_size else int((y-crop_size)/2)
        u = u[..., offset : -offset]
        v = v[..., offset : -offset]

        #Just in case there is still few pixels of size mismatch, resize
        u = cv2.resize(u, (crop_size,crop_size))
        v = cv2.resize(v, (crop_size,crop_size))

        gt_flow_resized = np.zeros((u.shape[0],u.shape[1],2))
        gt_flow_resized[...,0] = u
        gt_flow_resized[...,1] = v
    else:
        u = cv2.resize(gt_flow[...,0],(x,y))
        v = cv2.resize(gt_flow[...,1],(x,y))

        gt_flow_resized = np.zeros((u.shape[0],u.shape[1],2))
        gt_flow_resized[...,0] = u
        gt_flow_resized[...,1] = v

    pred_flow = flowpy.flow_read(args.predflowpath + predflow_path_list[i])

    #If predicted flow and processed GT flow dimensions do not match, interpolate predicted flow to have the same dimension as GT.
    if(u.shape[0] != pred_flow.shape[0] or u.shape[1] != pred_flow.shape[1]):
        pred_flow_resized = np.zeros((u.shape[0],u.shape[1],2))
        pred_flow_resized[...,0] = cv2.resize(pred_flow[...,0], u.shape)
        pred_flow_resized[...,1] = cv2.resize(pred_flow[...,1], v.shape)
    else:
        pred_flow_resized = pred_flow

    #If an event mask path is given, mask endpoint error inputs
    if args.maskenabled!='True':
        AEE_sum += avg_endpoint_error(gt_flow_resized, pred_flow_resized)
    else:
        mask = cv2.imread(args.maskpath + mask_path_list[i], cv2.IMREAD_GRAYSCALE)
        #If mask and resized predicted flow dimensions do not match, resize mask
        if (mask.shape[0] != pred_flow_resized.shape[0] or mask.shape[1] != pred_flow_resized.shape[1]):
            mask = cv2.resize(mask, pred_flow_resized[...,0].shape)
        AEE_sum += avg_endpoint_error_masked(gt_flow_resized, pred_flow_resized, mask)
    
if args.maskenabled!='True': print('AEE is NOT masked.')
else: print('AEE is masked.') 
print('AEE: %f' %(AEE_sum/total_number_flow))