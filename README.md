# StarTrack

### StarTrack is a modular Python package providing functionality for Astronomical image processing, star detection, and noise reduction. 

## Why is StarTrack useful?

Imaging objects in deep space is all about noise reduction. 

Many nebulae, galaxies and star clusters are extremely dim, and therefore long exposures are required to capture their detail. Due to the Earth's rotation it is necessary for an astronomic imaging system to be capable of tracking the night sky as an object moves. 

Any system like this will drift, as errors in tracking build up. Drift can cause stars to become badly distorted and for images to lose depth and clarity. 

To overcome this, one must take hundreds of individual images of a single object, each a few minutes in exposure, and "stack" these on top of each other to reduce the noise of the image and provide the equivalent of one very long exposure. 

Due to errors in tracking, these images will never be exactly aligned. There will be differences in their rotation, translation and scaling. If data is collected across differnet locations and times, the relative rotation and position of the object being captured will vary in captured data. 

## This is where StarTrack comes in. 

Startrack is built to combine hundreds of individual exposures of astronomical data, run star detection algorithms, and to identify reference points across many images. Using this information, it can "stack" these exposures together - identifying, aligning, and averaging every pixel in each individual frame to produce a stacked exposure which has a large reduction in noise. 

This stacked image can then be further image process to bring out features in the data such as intricate nebula patterns or distant supernovae in other far away galaxies.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/stacking_reference_frame_comparison.png" width="1000"/>

The example above compares a single frame (on the left) with 20 frames which have been aligned and stacked with StarTrack, showing the reduction in noise. 

StarTrack has been built without using any Computer Vision libraries (such as OpenCV), instead relying on manually derived algorithms written with NumPy, SciPy and scikit-learn.  
