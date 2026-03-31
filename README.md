
## What is StarTrack?

StarTrack is a modular object-oriented Python package providing functionality for Astronomical computer vision, star detection, and noise reduction. 
* Download the Python package here: [github.com/matthiasarndt/StarTrackRepository](https://github.com/matthiasarndt/StarTrackRepository/tree/master).
* Download example astronomical data of the Iris Nebula [here](https://www.dropbox.com/scl/fo/mxfl3nmta319p3rljnxh4/AKRRT-tVfRIa9Q5t6UU0wQ0?rlkey=csu6ess8s3lqmrlomypvjw8cv&st=s7sd0zm0&dl=0) to try the code.
* I have complied a brief slidepack on StarTrack [here](https://github.com/matthiasarndt/StarTrack/blob/main/Matthias_Arndt_Personal_Project_Python.pdf).
* The change log can be seen [here](https://github.com/matthiasarndt/StarTrack/blob/main/CHANGELOG.md).

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/m82_before_after_gif.gif" width="800"/>
</p>

An example GIF showing a single noisy input frame, which is then aligned and stacked against ~100 other frames to produce a denoised image, and is then colour-corrected with a built-in post processor!

## How has it been built? 

![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%235C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)

StarTrack has been built with manually derived Computer Vision algorithms designed in Python, with NumPy, SciPy and scikit-learn. The following technologies have been inplemented: 
* Object-Oriented Programming, Design Patterns (Pipeline), Inheritance & Composition
* Unsupervised Machine Learning (sci-kit learn), to detect, register, and classify stars and Astronomical features.
* Vectorised numerical methods and algorithms implemented with NumPy.
* Optimisation techniques (SciPy), used to automatically tune Image Processing parameters to allow the code to work across a large range of different image datasets.
* Dataclasses, to ensure a traceable flow of data and immutable inputs.
* Parallelisation and memory management to rapidly increase processing times and reduce RAM overhead.
* Code optimisation to reduce overall runtime.
* Regular version controlling with Git onto GitHub

## Why build StarTrack?

StarTrack aims to solve the biggest challenge in Deep Space Astronomy: reducing noise on extremely dim objects.  
* Many nebulae, galaxies and star clusters are extremely dim, and therefore long exposures are required to adequately capture their detail.
* Due to the Earth's rotation it is necessary for imaging systems to be capable of tracking the night sky.
* As tracking errors build up, drift becomes visible in captured images. Drift can cause stars to become distorted and for images to lose depth and clarity.
* To overcome this, hundreds of individual images (called frames) are taken of a single object, with each being exposed for a few minutes. These frames are then "stacked" on top of each other to reduce the noise of the overall image - thereby providing the equivalent of one very long exposure.
* Due to variations in tracking, none of the frames will be aligned exactly the same. There will be differences in their rotation, translation and scaling. Data collected across different geographic locations and times of the year can have particularly large variations in the relative position and rotation of a deep space object (DSO) in a frame. 

## How does it work?

StarTrack combines hundreds of individual exposures of astronomical data, often 10s of GigaBytes loaded in directly from a telescope, into a single image. This image can them be processed to reveal faint features of distant galaxies & nebulae. 

* StarTrack does this by running object detection algorithms and thereby identifying reference points across hundreds of individual frames. Using this information, it can "stack" these frames together - aligning and combining every pixel in each individual frame to produce a stacked exposure which has a large reduction in noise. 
* It can do this across many different deep space image datasets, by assessing the properties of a star field and tuning it's computer vision parameters as needed:

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/iris_and_horsehead.png" width="800"/>
</p>

## The Data Pipeline

Raw data goes through the following pipeline, concluding with the generation of a stacked frame. 

1. **Light Frame Processing**: All frames are imported and read in as LightFrame objects. These are processed to filter, count, and catalogue aligning stars inside an image. 
2. **Frame Alignment**: Each of the frames (on the order of 10s-100s of images) are aligned with the reference frame, which is the initial frame that all other layers are compared against. This involves calculating reference vectors for each image and warping/translating the data to match the reference frame. 
3. **Stacking**: As a result of frame alignment, a 3D array of data is created, where each layer represents one input frame which has been rotated/translated to match the reference frame. Data at each pixel co-ordinate are assessed and averaged to reduce noise and remove outliers.
4.  **Post-Processing**: The final stacked image is post-processed to remove gradients, neutralise the background, and apply colour correction. It applied unsupervised learning techniques and multi-dimensional curve fitting to do this. 
5.  **De-noising**: Currently WIP - with the aim to build a Variational Autoencoder CNN to compare raw data (in memory mapped form) with the final stacked image, producing "cleaned" and denoised input data. 

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/data_pipeline.png" width="800"/>
</p>

## 1. Light Frame Processing

### Star Isolation with Star Detection Parameter Tuning

Light frame processing involves numerical optimisation of search parameters for a variety of algorithms. The process is captured below. Please note this page is in development, and more details will soon be added!

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/ProcessingPipelineExample.png" width="1000"/>
</p>

### Star Detection with Machine Learning

Unsupervised machine learning is used to determine the number of stars identified, by labelling the resulting pixels into clusters. k_means is run for a large sweep of cluster numbers, and the silhouette score for each attempt is determined and used to identify the likely number of stars. 

The results from unsupervised learning are used to determine the centroids and bright pixel count (number of labels) in each cluster. This information is then plotted on the original monochrome frame, to show the n stars brightest stars which have been detected:  

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/stars_detected.png" width="800"/>
</p>

### Star Registration & Rejection

* Although the centroid information provided by unsuperivsed learning is broadly accurate, it only takes into account the brightest pixels of a star when determining it's centre.
* To get a more accurate estimate, which is required later during the alignment process, the following star cataloguing algorithm is used. In some occasions, clusters of small stars are mis-identified as a single large star. Additional algorithms are employed here to accurately identify the largest star in a cluster of stars. 
* A bounding box is drawn around each identified star, and the centre calculated based on an intensity mean average. This data is stored in a star catalogue, and is the main output of the image processing and star detection stage. The information is used in the following steps for frame alignment. 

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/star_cataloguing.png" width="600"/>
</p>

## 2. Frame Alignment

### Identifying Reference Points for Alignment using Euclidian Vector Matching Algorithms

All stars in a frame have their Euclidian vectors calculated in relation to all other stars:
* In the reference frame, against which all other frames are aligned, the largest star idenfitied is used as the reference point. 
* In all frames being aligned with the reference frame, each star is assessed from brightest to dimmest (with the brightest stars the most likely to match the reference star in the reference frame). For each star, the Euclidian vectors are compared against the vectors from the reference image.
* Once a match is found within a tolerance, the stars identified are logged as the reference stars and the reference point matching process is ended.
* These stars are used to align the reference and additional frames. 

<p align="center">
<img src="https://github.com/matthiasarndt/StarTrack/blob/main/figures/alignment_addition_frame.png" width="1100"/>
</p>

Note that to increase the robustness and reliability of this algorithms, more stars in additional alignment frames are identified than in the reference frame:
* If n stars are identified in the reference frame, 2n stars are identified in each additional alignment frame.
* This is to guarantee that the stars identified in the reference frame are also identified in the additional frames.
* Differences between frames, such as noise and the position of the target object in the frame, may change which stars are identified by the algorithms.
* Therefore in the additional frame more stars are identified than are needed to ensure overlap.

### Frame Translation & Rotation

Now that the co-ordinates of all alignment stars are known in each image, the image transformation can be undertaken to align them. An "affine" transformation (more information [here](https://en.wikipedia.org/wiki/Affine_transformation)), using scikit-learn, has been implemented.

An affine transformation has been used because images captured from an optical telescope (such as a refractor) may be subject to visual distortions (e.g. stretching near the edge of a frame), leading to non-linearities across a star field. 

## 3. Stacking

As of v0.3.3 of StarTrack, the only stacking method implemented reduces noise by taking a mean average of all aligned frames. Future releases will include other stacking methods which will reject pixels not within a set number of standard deviations from the mean (a technique called sigma clipping).

