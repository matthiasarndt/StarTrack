# StarTrack

### StarTrack is a modular object-oriented Python package providing functionality for Astronomical computer vision, star detection, and noise reduction. 
* Download the Python package [here](https://github.com/matthiasarndt/StarTrackRepository/tree/master).
* Download example astronomical data of the Iris Nebula [here](https://www.dropbox.com/scl/fo/mxfl3nmta319p3rljnxh4/AKRRT-tVfRIa9Q5t6UU0wQ0?rlkey=csu6ess8s3lqmrlomypvjw8cv&st=s7sd0zm0&dl=0) to try the code.
* I have complied a brief slidepack on StarTrack [here](https://github.com/matthiasarndt/StarTrack/blob/main/Matthias_Arndt_Personal_Project_Python.pdf).
* The change log can be seen [here](https://github.com/matthiasarndt/StarTrack/blob/main/changelog.md).

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/m82gif.gif" width="900"/>

### StarTrack has been built with manually derived Computer Vision algorithms designed in Python, with NumPy, SciPy and scikit-learn. The following technologies have been intgrated: 
* Object-Oriented Programming, Design Patterns (Pipeline), Inheritance & Composition
* Unsupervised Machine Learning (sci-kit learn), to detect, register, and classify stars and Astronomical features.
* Vectorised numerical methods and algorithms implemented with NumPy.
* Optimisation techniques (SciPy), used to automatically tune Image Processing parameters to allow the code to work across a large range of different image datasets.
* Dataclasses, to ensure a traceable flow of data and immutable inputs.
* Parallelisation and memory management to rapidly increase processing times and reduce RAM overhead.
* Code optimisation to reduce overall runtime.
* Regular version controlling with Git onto GitHub

## Why build StarTrack?

### StarTrack aims to solve the biggest challenge in Deep Space Astronomy: reducing noise on extremely dim objects.  
* Many nebulae, galaxies and star clusters are extremely dim, and therefore long exposures are required to adequately capture their detail.
* Due to the Earth's rotation it is necessary for imaging systems to be capable of tracking the night sky.
* As tracking errors build up, drift becomes visible in captured images. Drift can cause stars to become distorted and for images to lose depth and clarity.
* To overcome this, hundreds of individual images (called frames) are taken of a single object, with each being exposed for a few minutes. These frames are then "stacked" on top of each other to reduce the noise of the overall image - thereby providing the equivalent of one very long exposure.
* Due to variations in tracking, none of the frames will be aligned exactly the same. There will be differences in their rotation, translation and scaling. Data collected across different geographic locations and times of the year can have particularly large variations in the relative position and rotation of a deep space object (DSO) in a frame. 

## How does StarTrack solve these problems?

#### Startrack is built to combine hundreds of individual exposures of astronomical data - often 10s of GigaBytes of data read in directly from a telescope - into a single image.  

#### It accomplishes this by running star detection algorithms, and identifying reference points across many frames, and aligning them. Using this information, it can "stack" these exposures together - identifying, aligning, and averaging every pixel in each individual frame to produce a stacked exposure which has a large reduction in noise. 

## Data Pipeline

### Raw data goes through the following pipeline, concluding with the generation of a stacked frame. 

1. **Light Frame Processing**: All frames are imported and read in as LightFrame objects. These are processed to filter, count, and catalogue aligning stars inside an image. 
2. **Frame Alignment**: Each of the frames (on the order of 10s-100s of images) are aligned with the reference frame, which is the initial frame that all other layers are compared against. This involves calculating reference vectors for each image and warping/translating the data to match the reference frame. 
3. **Stacking**: As a result of frame alignment, a 3D array of data is created, where each layer represents one input frame which has been rotated/translated to match the reference frame. Data at each pixel co-ordinate are assessed and averaged to reduce noise and remove outliers. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/data_pipeline.png" width="800"/>

### There are three sections below, which each describe one of the main processing steps highlighted above and the respective algorithms implemented. 

## Light Frame Processing

The first step is to pre-process a single frame. Data is converted to be in 8-bit monochrome, and is then thresholded (to isolate stars) and blurred (Gaussian blur), to remove the effects of noise on the shapes of stars. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/ProcessingPipelineExample.png" width="1100"/>

### Image Processing Parameter Tuning

Next, a filter is run across this frame. At all co-ordinates in the frame where a bright pixel is identified (defined as a pixel of brightness = 255), the area sorrounding this pixel is searched for other bright pixels. 

The rationale behind this is that large stars are clusters of many bright pixels. 

This search algorithm has two parameters, the search radius, and the star detection count. Star detection count is the number of bright pixels within the search radius required for the algorithm to decide a star is present. 

If the number of pixels is above this threshold, it's location is stored. Once the filtering algorithm has been run, only the largest clusters of bright pixels remain. All small clusters of bright pixels are discarded. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/image_pipeline_2_crop_filtered.png" width="1100"/>

### Star Detection with Machine Learning

Unsupervised machine learning (k_means) is used to determine the number of stars identified, by assessing the clusters of pixels. k_means is run for a large sweep of cluster numbers, and the silhouette score for each attempt is stored. 

Silhouette score measures how well defined and different clusters are from each other. To identify the number of clusters in an image, the n_clusters estimate with the highest silhouette score is used. This is an alternative to elbow method, which assesses how the centroid error varies with estimates for n_clusters.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/stars_detected.png" width="475"/>

The results from unsupervised learning are used to determine the centroids and bright pixel count (number of labels) in each cluster. This information is then plotted on the original monochrome frame, to show the n stars brightest stars which have been detected:  

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/step_6_stars_overlaid.png" width="1100"/>

### Star Registration & Rejection

Although the centroid information provided by unsuperivsed learning is broadly accurate, it only takes into account the brightest pixels of a star when determining it's centre. To get a more accurate estimate, which is required later during the alignment process, the following star cataloguing algorithm is used.  

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/star_cataloguing.png" width="800"/>

A bounding box is drawn around each cluster centroid, and a light intensity based average of the monochrome data is inside this bounding box produces the the centre of a star. This centre estimate is baesd on the brightness of all pixels around the star. 

This data is stored in a star catalogue, and is the main output of the image processing stage and star detection stage. The information is used in the following steps for star identification and frame alignment.  

## Frame Alignment

### Alignment & Correlation Stars Identification

The largest star in the reference frame is labelled as the reference star. All other identified stars in the reference image are alignment stars. To identify these stars in other frames, the vector from each alignment star to the reference star is calculated.

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_reference_frame.png" width="1100"/>

In each additional frame an increased number of stars are identified. if n stars are identified in the reference frame, 2n stars are identified in each additional frame. This is to guarantee that the stars identified in the reference frame are also identified in the additional frames. Differences between frames, such as noise and the position of the target object in the frame, may change which stars are identified by the algorithms - and therefore in the additional frame more stars are identified than are needed to ensure overlap.

The stars identified are then cross referenced with alignment vectors from the reference image. 

<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_addition_frame.png" width="1100"/>

### Frame Translation & Rotation

Now that the co-ordinates of all alignment stars are known in each image, the image transformation can be undertaken to align them. An "affine" transformation (more information [here](https://en.wikipedia.org/wiki/Affine_transformation)), using scikit-learn, has been implemented.

An affine transformation has been used because images captured from an optical telescope (such as a refractor) may be subject to visual distortions (e.g. stretching near the edge of a frame), leading to non-linearities across a star field. 

## Stacking

As of v0.1 of StarTrack, the only stacking method implemented reduces noise by taking a mean average of all aligned frames. Future releases will include other stacking methods which will reject pixels not within a set number of standard deviations from the mean (a technique called sigma clipping).

## Future Features Roadmap

The following features will be integrated into StarTrack to improve functionality:

1) Further optimisation of existing codebase, with benchmarking for memory usage and time taken for each process to run. 
2) The addition of RGB processing capabilities. 
3) Implementation of post-processing capabilities for final stacked images (e.g. edge detection of nebulae, and dynamic range increases to bring out features of deep space objects). 
4) Machine Learning of final stacked image to further reduce noise using PyTorch. The aim here will be to use deep learning (Variational Autoenconders – VAE) to further reduce noise. 
5) Statistical analysis of pixels in each layer before they are “stacked” together. This will involve understanding the distribution of each pixel and using statistical approaches to remove noise and increase signal to noise ratio. 
6) GPU based computing to accelerate a lot of the algorithms which are currently CPU based. This will involve refactoring code to run off CuPy rather than NumPy or implementing computing with Numba. 
7) A GUI.
