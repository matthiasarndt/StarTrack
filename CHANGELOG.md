# Change Log

#### Version 0.3.4 - March 2026
* Introduced new "Config" module inside common for maintaining and documenting parameters for a specific dataset, e.g. tuned hyperparameters, solver parameters, and memory-mapped array sizes. This data will be required tor integration of the future denoising module into the wider codebase.
* Introduced functionality within "Config" module to write object attributes, such as the parameters listed above, to a JSON file. 
* Integrated parameter config into frame_stack module. 
* Renamed coupled_frames to frame_aligner to better represent its functionality.
* Reduced runtime of frame_stack code by optimising the class' __init__ method.
* Improved general legibility of code with docstrings and comments. 

#### Version 0.3.3 - March 2026
* Introduced new colour calibration algorithms.
* Implemented cumulative distribution matching functionality to align RGB channels. This approach works well for aligning colour channels to restore overall white balance for cameras that have been modified.
* The existing colour calibration method from v0.3.0 has been renamed to neutralise_background. It has been refactored to focus on removing the effect of light pollution. Otherwise the method is unchanged. 
* Improved background neutralisation by improving least squares 2D curve fitting of lens distortions to take into account linear gradients caused by light pollution.
* Built-in visualisation functionality for histograms.

#### Version 0.3.2 - March 2026
* Created FrameTuner, a module responsible for all LightFrame hyperparameter tuning, under the FrameStack module.
* Moved all tuning logic from LightFrame to FrameTuner.
* Refactored FrameStack to integrate the new FrameTuner module.
* Reduced the tolerance required for the bisection optimisation solver logic in FrameTuner to converge, resulting in faster optimisation of LightFrame hyperparameters. 
* Improved general legibility of code with docstrings and comments. 

#### Version 0.3.1 - March 2026
* Renamed StackedImage to PostProcessor.
* Refactored LightFrame to split functionality into private methods and improve legibility. 
* Fixed bug causing automatic threshold tuning process in LightFrame to produce an error. 
* Created denoiser module (currently empty). This will include the following objects for CNN deep learning for denoising: dataset, model, train, inference. 
* Improved general legibility of code with docstrings and comments. 

#### Version 0.3.0 - January 2026
* Introduced new StackedImage module, which provides image processing capabilities to stacked images produced by the FrameStack class.
* Implemented colour correction, background identification, vignette removal, and dynamcic range adjustment codes.
* Background identification has been implemented with 5D HDBSCAN clustering to identify regions of similarity.
* Vignette remvoal has been designed using least squares curve fitting algorithms to approximate the curvature of an image.
* Improved general legibility of code with docstrings and comments. 

#### Version 0.2.5 - November 2025:
* Reduced memory usage for frame alignment process by ~75% by re-architecting the FrameRead and CoupledFrames class. This includes only reading RGB data when required, and otherwise not storing it on memory.
* Introduced memory profiling to better understand which sections of the code are the most RAM intensive.  
* Restructured the code so that CoupledFrames is now called FrameAligner, and AstroPhoto is now called FrameStack, to better reflect the objects that are being manipulated. FrameAligner is now located within the FrameStack folder.
* Refactored FrameAligner, introducing a new class called AlignmentVectorMatcher, replaing the existing static method with a dedicated class for matching alignment vectors between two frames. The current method is based on a rank search, and in the future additional methods will be added.
* Introduced new class called StackingMethods, within FrameStack, which is currently not implemented. Future releases will include additional stacking methods, e.g. median or a weighted average. 
* Introduced new folder for StackedImage class, with methods and properties for stacked image manipulation to be added in the future. 
* Improved general legibility of code with additional function descriptions and comments. 

#### Version 0.2.4 - October 2025:
* Implemented memory mapped arrays to store aligned frames on a disk rather than on memory, to reduce overall memory usage whilst processing data.
* Implemented saving of tuned parameters to .JSON files for a specific image dataset. If a user re-runs the code on this dataset, the code will ask the user if they wish to reuse previously tuned parameters - allowing for signficant time savings!
* Refactored stacking method inside AstroPhoto to load in chunks from the memory mapped array, and process set of data at a time. 
* Generally refactored AstroPhoto for improved clarity and breakdown of functionality, and optimised/reduced memory usage and processing.
* Added functionality to store output final stacked frame in 16-bit format as a .TIFF. This allows for a greater amount of dynamic range to be captured from the stacking methods, and means less data will be lost as a result. 

#### Version 0.2.3 - October 2025:
* Implemented new functionality to process data in Red, Green and Blue channels - allowing for RGB images to be processed.
* Integrated parameter tuning for thresholding when reading new images into wider code. The functionality to do this was introduced in the previous update (v0.2.2). 
* Refactored the star_field class, with code restructured for improved readibility and variables renamed for better clarity. The framework for a future method to remove asymmetrical stars from dedection was also introduced. 
* Refactored astro_photo class to split stacking and initialisation functionalities into two seperate methods.
* Reduced memory overhead required by ensuring only required data is held in memory. 
* Added new "utils" class, inside the light_frame class, which will be populated with commonly re-used functionality. So far the local_density_filter has been implemented.  

#### Version 0.2.2 - October 2025:
* Implemented new functionality to automatically tune the correct required threshold level when reading in a frame. This is based on the overall brightness of an image and the density of stars. This parameter is currently set manually. In a future release, threshold tuning will be further integrated to run automatically if no threshold value is specified in the initial inputs.
* Created a slidepack detailing StarTrack and how it works, see [here](https://github.com/matthiasarndt/StarTrack/blob/main/Matthias_Arndt_Personal_Project_Python.pdf).
* Improved parallelisation process so that a failed frame alignment will no longer kill the pool, and keeps the code running.
* Improved diagnostics & update printing, to state when a frame alignment has failed. 
* Further reduced memory usage during stacking process by using 8 bit integers where possible, rather than 64 bit integers as before. 
* Added new "common" class, with a logo and version number. This logo can now be printed. 
* Fixed bug which meant the first addition alignment frame data wasn't being stored and used for stacking. 
* Fixed bug which meant the reference frame and first additon alingment frame process_with_solver initialisation code wasn't running in parallel. 

#### Version 0.2.1 - September 2025:
* Implemented star reduction solving algorithm, using line solving and gradient descent based methods to isolate a single bright star in a cluster of bright stars. This has made star registration far more robust.
* Implemented parallelisation, massively improving performance of star registration, alignment, and stacking process.
* Refactored code to reduce memory usage and improve garbage collection to improve parallelisation on reduced memory.
* Improved star_field class, with code refactoring, new functions, improved comments, and reduced results printing. 
* Improved example.py code with new and improved comments on input settings. 

#### Version 0.2 - September 2025:
* Implemented new star cataloguing algorithms, improving star detection by removing object and filtering objects falsely identified as a single bright star.
* Implemented new star alignment algorithms to account for distance and angle of an alignment star from the reference alignment star, allowing for more reliable star identification.
* Improved star alignment with new star analysis algorithms. Rather than assuming the largest star is always the reference alignment star, stars are analysed in descending order of size until a match is made. Improves robustness of image alignment and stacking for noisy images, where star size may vary significantly. 
* Reduced time to determine min_star_num required in star_filter to find the n brightest stars, by changing numerical methods from non_linear least squares to bisection and optimising unsupervised machine learning (see below).
* Optimised unsupervised machine learning, significantly reducing runtimes, by down sampling large datasets when calculating silhouette score and additionally implementing mini k means to reduce overall sample size. 
* Added new comments and debugging/verbosity printing.
* Added support for more image formats: Nikon RAW (.NEF) and .PNG. 
* General bugfixes and code improvements (refactoring, variable naming).

#### Version 0.1 - August 2025:
- Initial working version, with astro_photo, coupled_frames, and light_frame classes.
