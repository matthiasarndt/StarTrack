### Version 0.2:
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
