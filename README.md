# eventUtils
Event-based vision utility scripts.
* **preprocess:** Preprocessing of frames. Consists of resizing, downsampling and cropping, all in batches.
* **bag2hdf5:** Converts a .rosbag file containing events into a .hdf5. [MVSEC dataset](https://daniilidis-group.github.io/mvsec/) is taken as a guideline for the data organization.
* **bag2img:** Extracts image_raw data from a rosbag file.
* **img2hdf5:** Writes grayscale image data read from a directory into an existing hdf5 file.
* **flow2hdf5:** Writes .flo files read from a directory into a new hdf5 file, with the corresponding timestamps to the output of bag2hdf5.py.
* **auto.bash:** Runs all necessary scripts for:
    * Pre-processing (resizing,downsampling etc.) high framerate images and their flow files
    * Generating events in rosbag format via [ESIM](https://github.com/uzh-rpg/rpg_esim) using processed images & flows 
    * Converting rosbag dataset into hdf5
    * Split encoding of data in hdf5 file (part of [Spike-FlowNet](https://github.com/chan8972/Spike-FlowNet))

* Must run roscore in another terminal beforehand for auto.bash.
