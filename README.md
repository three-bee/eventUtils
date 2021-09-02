# eventUtils
Event-based vision utility scripts.
* **bag2hdf5:** Converts a .rosbag file containing events into a .hdf5. [MVSEC dataset](https://daniilidis-group.github.io/mvsec/) is taken as a guideline for the data organization.
* **bag2img:** Extracts image_raw data from a rosbag file.
* **img2hdf5:** Writes grayscale image data read from a directory into an existing hdf5 file.
* **flow2hdf5:** Writes .flo files read from a directory into a new hdf5 file, with the corresponding timestamps to the output of bag2hdf5.py.
