# StarTrack

### StarTrack is a modular object-oriented Python package providing functionality for Astronomical image processing, star detection, and noise reduction. 
* Download the Python package [here](https://github.com/matthiasarndt/StarTrack/blob/main/StarTrack_v0.1.zip).
* Download example astronomical data of the Iris Nebula [here](https://www.dropbox.com/scl/fo/mxfl3nmta319p3rljnxh4/AKRRT-tVfRIa9Q5t6UU0wQ0?rlkey=csu6ess8s3lqmrlomypvjw8cv&st=s7sd0zm0&dl=0) to use the code yourself!

## Why is StarTrack useful?

The biggest challenge in deep space astronomy imaging is noise reduction. 

Many nebulae, galaxies and star clusters are extremely dim, and therefore long exposures are required to adequately capture their detail. Due to the Earth's rotation it is necessary for imaging systems to be capable of tracking the night sky.

As tracking errors build up, drift becomes visible in captured images. Drift can cause stars to become distorted and for images to lose depth and clarity. 

To overcome this, hundreds of individual images (called frames) are taken of a single object, with each being exposed for a few minutes. These frames are then "stacked" on top of each other to reduce the noise of the overall image - thereby providing the equivalent of one very long exposure. 

Due to variations in tracking, none of the frames will be aligned exactly the same. There will be differences in their rotation, translation and scaling. Data collected across different geographic locations and times of the year can have particularly large variations in the relative position and rotation of a deep space object (DSO) in a frame. 

## This is where StarTrack comes in!

Startrack is built to combine hundreds of individual exposures of astronomical data. It does this by running star detection algorithms, and identifying reference points across many frames, and aligning them. Using this information, it can "stack" these exposures together - identifying, aligning, and averaging every pixel in each individual frame to produce a stacked exposure which has a large reduction in noise. 

### StarTrack has been built without using any Computer Vision libraries (such as OpenCV), instead relying on algorithms derived from scratch, written with NumPy, SciPy and scikit-learn. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/reference_to_stacked_gif.gif" width="500"/>

The example above compares a single frame (on the left) with 20 frames which have been aligned and stacked with StarTrack, showing the reduction in noise. This stacked image can then be further image process to bring out features in the data.

## Code Structure

The code has been developed and structured with Object-Orientation. Classes and methods have been written with design patterns in mind (specifically a Pipeline design pattern), and use inheritance and composition.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/code_structure.png" width="500"/>

## Data Pipeline

## Initial Image Processing

### Overview

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/frame_processing_pipeline.png" width="1100"/>

### Local Density Filter & Numerical Solving for Search Parameter Optimisation 

## Unsupervised Machine Learning for Star Detection

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/step_5_identify_n_clusters.png" width="400"/>

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/step_6_stars_overlaid.png" width="400"/>

## Star Cataloguing with Intensity based Weighted Averaging

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/star_cataloguing.png" width="800"/>

## Alignment using Vectors

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_reference_frame.png" width="1100"/>

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_addition_frame.png" width="1100"/>

## Stacking

