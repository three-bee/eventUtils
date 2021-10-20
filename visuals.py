import h5py
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

parser = argparse.ArgumentParser()
parser.add_argument('--hdf5path', type=str, help='Path of hdf5 file')
args = parser.parse_args()

fig = plt.figure()
ax = fig.add_subplot(312, projection='3d')
ax2 = fig.add_subplot(311, projection='3d')
ax3 = fig.add_subplot(313, projection='3d')

with h5py.File(args.hdf5path,"r") as dataset:
    arr = dataset['davis']['left']['events'][()]
    arr = np.transpose(arr)

    #Only show event_number amount of events on the plot, chosen randomly
    event_number = 3000
    event_range = 41000 - 21000
    indx = np.random.choice(event_range,event_number,False)
    events_x = arr[0][21000:41000][indx]
    events_y = arr[1][21000:41000][indx]
    timestamp = arr[2][21000:41000][indx]
    polarity = arr[3][21000:41000][indx]

    ax.scatter(timestamp[polarity==1], events_x[polarity==1],-events_y[polarity==1],c='b',s=1)
    ax.scatter(timestamp[polarity==-1], events_x[polarity==-1],-events_y[polarity==-1],c='r',s=1)

    img1 = plt.imread("/home/bbatu/SINTEL/sintel_data_1008fps/clean_1008fps/ambush_2/resized/cropped/cropped000.png")
    img2 = plt.imread("/home/bbatu/SINTEL/sintel_data_1008fps/clean_1008fps/ambush_2/resized/cropped/cropped001.png")

    yy,zz = np.meshgrid(range(img1.shape[0]), range(img1.shape[1]))
    xx = yy*0

    ax2.plot_surface(2e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax2.plot_surface(2.4e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax2.plot_surface(2.8e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax2.plot_surface(3.2e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax2.plot_surface(3.6e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax2.plot_surface(4e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)

    ax.plot_surface(2e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax.plot_surface(4e7,yy,-zz,rstride=1, cstride=1,facecolors=img2)

    ax3.plot_surface(2e7,yy,-zz,rstride=1, cstride=1,facecolors=img1)
    ax3.plot_surface(4e7,yy,-zz,rstride=1, cstride=1,facecolors=img2)

    ax.view_init(15, -75)
    ax2.view_init(15, -75)
    ax3.view_init(15, -75)
    
    ax.axis('off')
    ax2.axis('off')
    ax3.axis('off')

    plt.subplot_tool()

    plt.show()