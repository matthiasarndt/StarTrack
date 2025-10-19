The next version (0.2.5) will focus on the introduction of additional image processing tools (e.g. white balancing an image), a refactoring of the AstroPhoto class to introduce subclasses, and an update to the FrameReader class. 

#### Version 0.2.4:
* Implementeed memory mapped arrays to store aligned frames on a disk rather than on memory, to reduce overall memory usage whilst processing data.
* Refactored stacking method inside AstroPhoto to load in chunks from the memory mapped array, and process set of data at a time. 
* Generally refactored AstroPhoto for improved clarity and breakdown of functionality, and optimised/reduced memory usage and processing.
* Added functionality to store output final stacked frame in 16-bit format as a .TIFF. This allows for a greater amount of dynamic range to be captured from the stacking methods, and means less data will be lost as a result. 

#### Version 0.2.3:
* Implemented new functionality to process data in Red, Green and Blue channels - allowing for RGB images to be processed.
* Integrated parameter tuning for thresholding when reading new images into wider code. The functionality to do this was introduced in the previous update (v0.2.2). 
* Refactored the star_field class, with code restructured for improved readibility and variables renamed for better clarity. The framework for a future method to remove asymmetrical stars from dedection was also introduced. 
* Refactored astro_photo class to split stacking and initialisation functionalities into two seperate methods.
* Reduced memory overhead required by ensuring only required data is held in memory. 
* Added new "utils" class, inside the light_frame class, which will be populated with commonly re-used functionality. So far the local_density_filter has been implemented.  

#### Version 0.2.2:
* Implemented new functionality to automatically tune the correct required threshold level when reading in a frame. This is based on the overall brightness of an image and the density of stars. This parameter is currently set manually. In a future release, threshold tuning will be further integrated to run automatically if no threshold value is specified in the initial inputs.
* Created a slidepack detailing StarTrack and how it works, see [here](https://github.com/matthiasarndt/StarTrack/blob/main/Matthias_Arndt_Personal_Project_Python.pdf).
* Improved parallelisation process so that a failed frame alignment will no longer kill the pool, and keeps the code running.
* Improved diagnostics & update printing, to state when a frame alignment has failed. 
* Further reduced memory usage during stacking process by using 8 bit integers where possible, rather than 64 bit integers as before. 
* Added new "common" class, with a logo and version number. This logo can now be printed. 
* Fixed bug which meant the first addition alignment frame data wasn't being stored and used for stacking. 
* Fixed bug which meant the reference frame and first additon alingment frame process_with_solver initialisation code wasn't running in parallel. 

#### Version 0.2.1:
* Implemented star reduction solving algorithm, using line solving and gradient descent based methods to isolate a single bright star in a cluster of bright stars. This has made star registration far more robust.
* Implemented parallelisation, massively improving performance of star registration, alignment, and stacking process.
* Refactored code to reduce memory usage and improve garbage collection to improve parallelisation on reduced memory.
* Improved star_field class, with code refactoring, new functions, improved comments, and reduced results printing. 
* Improved example.py code with new and improved comments on input settings. 

#### Version 0.2:
* Implemented new star cataloguing algorithms, improving star detection by removing object and filtering objects falsely identified as a single bright star.
* Implemented new star alignment algorithms to account for distance and angle of an alignment star from the reference alignment star, allowing for more reliable star identification.
* Improved star alignment with new star analysis algorithms. Rather than assuming the largest star is always the reference alignment star, stars are analysed in descending order of size until a match is made. Improves robustness of image alignment and stacking for noisy images, where star size may vary significantly. 
* Reduced time to determine min_star_num required in star_filter to find the n brightest stars, by changing numerical methods from non_linear least squares to bisection and optimising unsupervised machine learning (see below).
* Optimised unsupervised machine learning, significantly reducing runtimes, by down sampling large datasets when calculating silhouette score and additionally implementing mini k means to reduce overall sample size. 
* Added new comments and debugging/verbosity printing.
* Added support for more image formats: Nikon RAW (.NEF) and .PNG. 
* General bugfixes and code improvements (refactoring, variable naming).

#### Version 0.1:
- Initial working version, with astro_photo, coupled_frames, and light_frame classes.
