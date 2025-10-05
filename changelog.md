### Version 0.2.1:
* Implemented new functionality to automatically tune the correct required threshold level when reading in a frame. This is based on the overall brightness of an image and the density of stars. This parameter is currently set manually. In a future release, the threshold tuning will be further integrated.
* Created a slidepack detailing StarTrack and how it works, see [here](https://github.com/matthiasarndt/StarTrack/blob/main/Matthias_Arndt_Personal_Project_Python.pdf).
* Improved parallelisation process so that a failed frame alignment will no longer kill the pool, and keep the code running.
* Improved diagnostics & update printing, to state when a frame alignment has failed. 
* Further reduced memory usage during stacking process by using 8 bit integers where possible, rather than 74 bit integers as before. 
* Added new "common" class, with a logo and version number stored. This logo is now printed. 
* Fixed bug which meant the first addition alignment frame data wasn't being stored and used for stacking. 
* Fixed bug which meant the reference frame and first additon alingment frame process_with_solver initialisation code wasn't running in parallel. 

### Version 0.2.1:
* Implemented star reduction solving algorithm, using line solving and gradient descent based methods to isolate a single bright star in a cluster of bright stars. This has made star registration far more robust.
* Implemented parallelisation, massively improving performance of star registration, alignment, and stacking process.
* Refactored code to reduce memory usage and improve garbage collection to improve parallelisation on reduced memory.
* Improved star_field class, with code refactoring, new functions, improved comments, and reduced results printing. 
* Improved example.py code with new and improved comments on input settings. 

### Version 0.2.0:
* Implemented new star cataloguing algorithms, improving star detection by removing object and filtering objects falsely identified as a single bright star.
* Implemented new star alignment algorithms to account for distance and angle of an alignment star from the reference alignment star, allowing for more reliable star identification.
* Improved star alignment with new star analysis algorithms. Rather than assuming the largest star is always the reference alignment star, stars are analysed in descending order of size until a match is made. Improves robustness of image alignment and stacking for noisy images, where star size may vary significantly. 
* Reduced time to determine min_star_num required in star_filter to find the n brightest stars, by changing numerical methods from non_linear least squares to bisection and optimising unsupervised machine learning (see below).
* Optimised unsupervised machine learning, significantly reducing runtimes, by down sampling large datasets when calculating silhouette score and additionally implementing mini k means to reduce overall sample size. 
* Added new comments and debugging/verbosity printing.
* Added support for more image formats: Nikon RAW (.NEF) and .PNG. 
* General bugfixes and code improvements (refactoring, variable naming).

### Version 0.1: 
- Initial working version, with AstroPhoto, CoupledFrames, and LightFrame classes.
