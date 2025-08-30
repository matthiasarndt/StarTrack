# StarTrack

### StarTrack is a modular Python package providing functionality for Astronomical image processing, star detection, and noise reduction. 
* Download the Python package [here](https://github.com/matthiasarndt/StarTrack/blob/main/StarTrack_v0.1.zip)
* Download astronomical data of the Iris Nebula [here](https://www.dropbox.com/scl/fo/mxfl3nmta319p3rljnxh4/AKRRT-tVfRIa9Q5t6UU0wQ0?rlkey=csu6ess8s3lqmrlomypvjw8cv&st=s7sd0zm0&dl=0) to use the code.

## Why is StarTrack useful?

Imaging objects in deep space is all about noise reduction. 

Many nebulae, galaxies and star clusters are extremely dim, and therefore long exposures are required to capture their detail. Due to the Earth's rotation it is necessary for an astronomic imaging system to be capable of tracking the night sky as an object moves. 

Any system like this will drift, as errors in tracking build up. Drift can cause stars to become badly distorted and for images to lose depth and clarity. 

To overcome this, one must take hundreds of individual images of a single object, each a few minutes in exposure, and "stack" these on top of each other to reduce the noise of the image and provide the equivalent of one very long exposure. 

Due to errors in tracking, these images will never be exactly aligned. There will be differences in their rotation, translation and scaling. If data is collected across differnet locations and times, the relative rotation and position of the object being captured will vary in captured data. 

## This is where StarTrack comes in. 

Startrack is built to combine hundreds of individual exposures of astronomical data, run star detection algorithms, and to identify reference points across many images. Using this information, it can "stack" these exposures together - identifying, aligning, and averaging every pixel in each individual frame to produce a stacked exposure which has a large reduction in noise. 

This stacked image can then be further image process to bring out features in the data such as intricate nebula patterns or distant supernovae in other far away galaxies.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/reference_to_stacked_gif.gif" width="800"/>

The example above compares a single frame (on the left) with 20 frames which have been aligned and stacked with StarTrack, showing the reduction in noise. 

StarTrack has been built without using any Computer Vision libraries (such as OpenCV), instead relying on algorithms derived from scratch, written with NumPy, SciPy and scikit-learn. 

## Code Structure

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

## Stacking

