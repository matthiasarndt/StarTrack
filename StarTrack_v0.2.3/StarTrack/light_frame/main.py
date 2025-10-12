
# dependencies
from scipy.optimize import least_squares, fsolve, bisect
from StarTrack.light_frame.star_field import Starfield
from StarTrack.light_frame.star_alignment_vectors import StarAlignmentVectors
from StarTrack.light_frame.star_filter import StarFilter
from StarTrack.light_frame.frame_reader import FrameReader
from dataclasses import dataclass
from pathlib import Path
from dataclasses import replace

class LightFrame:

    # define inputs as a data class which is frozen
    @dataclass(frozen=True)
    class FrameInputs:

        # default inputs, where possible, are written below
        frame_name: str
        frame_directory: Path
        threshold: int = 254

        # inputs are ordered so that those without a default value go first
        verbosity: int = 0
        star_detect_radius: int = 20
        star_detect_pixels: int = 50
        crop_factor: float = 0.85
        blur_radius: float = 3

    def __init__(self, **kwargs):
        # import inputs from dataclass
        self.inputs = self.FrameInputs(**kwargs)

        # intermediates
        self.threshold_array = None
        self.mono_array = None
        self.cluster_array = None

        # outputs
        self.pixels_in_clusters = None
        self.n_clusters = None
        self.centroid_list = None
        self.magnitude_list = None
        self.ref_vectors = None
        self.ref_angles = None
        self.ref_star = None
        self.i_ref_star = None
        self.non_ref_stars = None

    # tune to provide a good thresholding value
    def tune_threshold(self):

        # implementation of a line solver, reducing threshold from 254 at increments of 4
        # stop when an acceptable spread of stars is found between min_star_radius 1000 (?) & 1
        # return just this value
        # find a way to integrate this result into the rest of the code

        # threshold will be set to -1 by default, which will run this code.
        # this code should only be run if self.inputs.threshold = -1, if not, it can be ignored
        # later check if self.inputs.threshold is -1
        # if it is, use the value found here.
        # if not, use the value predefined

        def fitness_function(x):

            def evaluate_threshold(star_detect_pixels,count,case):

                # try a new input, with an updated star_detect_pixels
                self.inputs = replace(self.inputs, star_detect_pixels=star_detect_pixels, threshold=x)

                # run processing and find residual
                print(f"ATTEMPTING THRESHOLD: {threshold_iteration}")
                FrameReader(self).pre_process()
                StarFilter(self).local_density()

                # assume high residual
                z = 1000

                # only run this if pixels are detected
                if len(self.pixels_in_clusters) > 0:
                    # count stars
                    Starfield(self).count_stars()

                    # assess results
                    if case == "upper_bound":
                        if self.n_clusters > count:
                            z = 0
                        else:
                            z = abs(self.n_clusters - count)
                        #print(f"upper bound residual: {z}")

                    if case == "lower_bound":
                        if self.n_clusters < count:
                            z = 0
                        else:
                            z = abs(self.n_clusters - count)
                        #print(f"lower bound residual: {z}")

                return z

            # evaluate star detections & resulting residuals at extreme limits
            min_radius_residual = evaluate_threshold(star_detect_pixels=10,count=50,case="upper_bound")
            max_radius_residual = evaluate_threshold(star_detect_pixels=1000,count=5,case="lower_bound")

            total_residual = min_radius_residual + max_radius_residual

            return total_residual

        # initialise
        iterate = True
        threshold_iteration = 254
        threshold_reduction = 4
        residual = fitness_function(threshold_iteration)
        print(residual)
        if residual == 0: iterate = False

        # continue to calculate values until the residual drops to 0
        while iterate:

            # increase the value of the star detection radius:
            threshold_reduction = threshold_reduction * 1.05
            threshold_iteration = threshold_iteration - threshold_reduction

            residual = fitness_function(threshold_iteration)
            print(residual)

            if residual == 0:
                iterate = False

        return int(threshold_iteration)

    # find the minium search radius required to find n clusters
    def tune_star_detect_pixels(self, n_desired_clusters):

        # fitness function which is passed through the least squares optimiser
        def fitness_function(x):

            # try a new input, with an updated star_detect_pixels
            self.inputs = replace(self.inputs, star_detect_pixels=x)

            # run processing and find residual
            StarFilter(self).local_density()

            if len(self.pixels_in_clusters) > 0:
                Starfield(self).count_stars()
                residual = n_desired_clusters - self.n_clusters
            else:
                residual = 100

            # debugging information
            if __name__ == "__main__":
                print(f"Residual = {residual}, from star_detect_pixels = {x}")

            return residual

        # read in the image
        FrameReader(self).pre_process()

        # bisection solving to determine ideal star detection threshold inside search radius
        result = bisect(fitness_function, 1, 1000)

        # return an optimum minimum star count
        return result

    # process light frame
    def process(self):
        FrameReader(self).pre_process()
        StarFilter(self).local_density()
        Starfield(self).count_stars()
        Starfield(self).catalogue_detected_stars()
        StarAlignmentVectors(self).from_biggest_star()

        return self

    # process light frame and tune star_detect_pixels to the correct value
    def process_tuning_star_detect(self, n_desired_clusters):
        tuned_star_detect_pixels = self.tune_star_detect_pixels(n_desired_clusters) # calls FilterImage and CatalogueClusters to do this
        Starfield(self).catalogue_detected_stars()
        StarAlignmentVectors(self).from_biggest_star()

        return tuned_star_detect_pixels

if __name__ == "__main__":
    data_dir = Path(r"D:\_Local\OneDrive\Astronomy\StarTrack\dev\raw_data_iris_nebula")
    verbosity = 1
    #light = LightFrame(frame_directory=data_dir, frame_name="iris_nebula_frame_2.jpg", verbosity=verbosity)
    #t_tuned = light.tune_threshold()
    light = LightFrame(frame_directory=data_dir, frame_name="iris_nebula_frame_2.jpg", verbosity=verbosity, star_detect_pixels=500.5, threshold=231)
    light.process()
    temp = 5