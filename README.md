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

### StarTrack has been built without any Computer Vision libraries (such as OpenCV), instead relying on algorithms derived from scratch, written with NumPy, SciPy and scikit-learn. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/reference_to_stacked_gif.gif" width="500"/>

The example above compares a single frame (on the left) with 20 frames which have been aligned and stacked with StarTrack, showing the reduction in noise. This stacked image can then be further image process to bring out features in the data.

## Code Structure

The code has been developed and structured with Object-Orientation. Classes and methods have been written with design patterns in mind (specifically a Pipeline design pattern), and use inheritance and composition. Inputs into the code use dataclasses, which are frozen to avoid mutability and keep the flow of data tracable. 

The three classes are LightFrame, CoupledFrames, and AstroPhoto. AstroPhoto is the highest level class, and is called by the user. Each class has the following functionality:
* LightFrame: reading of raw data, processing of raw data, star detection, star cataloguing
* CoupledFrame:identification of alignment stars and frame alignment between two LightFrame instances 
* AstroPhoto: wrapper for all functionality, running algorithms to process, align, and stack all frames  

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/code_structure.png" width="500"/>

## Data Pipeline

Raw data goes through the following pipeline, concluding with the generation of a stacked frame. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/data_pipeline.png" width="800"/>

There are three sections below, which each describe one of the main processing steps highlighted above and the respective algorithms implemented. 

## Light Frame Processing

### 1. Initial Image Processing

The first step is to pre-process a single frame. Data is converted to be in 8-bit monochrome, and is then thresholded (to isolate stars) and blurred (Gaussian blur), to remove the effects of noise on the shapes of stars. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/image_pipeline_1_mono_threshold_blur.png" width="1100"/>

### 2. Image Filtering & Star Detection Parameter Optimisation

Next, a filter is run across this image. At all pixel co-ordinates in the image where a bright pixel is identifed (defined as a pixel of brightness = 255), an area is searched sorrounding this pixel to search for other bright pixels. 

The rationale is that large stars are clusters of many bright pixels. 

This search algorithm has two parameters, the search radius, and the star detection count (the number of bright pixels within the search radius required for the algorithm to decide a star is present). 

If the number if pixels is above this threshold, it's location is stored. Once the filtering algorithm has been run, only the largest clusters of bright pixels remain. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/image_pipeline_2_crop_filtered.png" width="1100"/>

### 3. Unsupervised Machine Learning for Star Detection

Unsupervised machine learning (k_means) is used to determine the number of stars identified, by assessing the clusters of pixels. k_means is run for a large sweep of cluster numbers, and the silhouette score for each attempt is stored. 

Silhouette score measures how well defined and different clusters are from each other. To identify the number of clusters in an image, the n_clusters estimate with the highest silhouette score is used. This is an alternative to elbow method, which assesses how the centroid error varies with estimates for n_clusters.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/step_5_identify_n_clusters.png" width="475"/>

The results from unsupervised learning are used to determine the centroids and bright pixel count (number of labels) in each cluster. This information is then plotted on the original monochrome frame, to show the n stars brightest stars which have been detected:  

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/step_6_stars_overlaid.png" width="1100"/>

### 4. Numerical Solving to Optimise Search Parameters 

The two algorithms above (unsupervised machine learning and filtering) are used to find the n largest stars in an image. 

To do this, the search parameters must be tuned so that they discard the right amount of stars. This tuning will be different for every part of the night sky, as the density of stars varies. The tuning has been implemented with a numerical solver. Here, a bisection solver has been used to determine the star detection count within a given radius which will give the largest n stars. n can vary but is typically set to 5.  

### 5. Star Cataloguing

Although the centroid information provided by unsuperivsed learning is broadly accurate, it only takes into account the brightest pixels of a star when determining it's centre. To get a more accurate estimate, which is required later during the alignment process, the following star cataloguing algorithm is used.  

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/star_cataloguing.png" width="800"/>

A bounding box is drawn around each cluster centroid, and a light intensity based average of the monochrome data is inside this bouding box is used to find the centre of a star based on the brightness of all pixels inthe star. 

This data is stored in a star catalogue, and is the main output of the image processing stage and star detection stage. The information is used in the following steps for star identification and frame alignment.  
## Frame Alignment

### 1. Alignment Star Identification

The largest star in the reference frame is labelled as the reference star. All other identified stars in the reference image are alignment stars. To identify these stars in other images, the vector from each alignment star to the reference star is calculated.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_reference_frame.png" width="1100"/>

In each additional frame, an increased number of stars are identified. if n stars are identified in the reference image, 2n stars are identified in each additional image. This is to guarantee that the stars identified in the reference image are also identified in the additional frames. Differences between frames, such as noise and the position of the target object in the frame, may change which star are identified by the algorithm - and therefore in the additional frame more stars are identified than are needed. 

The stars identified are then cross referenced with alignment vectors from the reference image. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_addition_frame.png" width="1100"/>

### 2. Frame Translation & Rotation

Now that the co-ordinates of all alignment stars are known in each image, the image transformation can be undertaken to align them. An "affine" transformation (more information [here](https://en.wikipedia.org/wiki/Affine_transformation)), using scikit-learn, has been implemented.

An affine transformation has been used because images captured from an optical telescope (such as a refractor) may be subject to visual distortions (e.g. stretching near the edge of a frame), leading to non-linearities across a star field. 

## Stacking

As of v0.1 of StarTrack, the only stacking method implemented reduces noise by taking a mean average of all aligned frames. Future releases will include other stacking methods which will reject pixels not within a set number of standard deviations from the mean (a technique called sigma clipping).
