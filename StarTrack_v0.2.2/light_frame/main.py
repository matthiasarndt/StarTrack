
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
        # inputs are ordered so that those without a default value go first
        verbosity: int = 0
        star_detect_radius: int = 20
        min_star_num: int = 50
        threshold_value: int = 250
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

            def evaluate_threshold(min_star_num,count,case):

                # try a new input, with an updated min_star_num
                self.inputs = replace(self.inputs, min_star_num=min_star_num, threshold_value=x)

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
            min_radius_residual = evaluate_threshold(min_star_num=10,count=50,case="upper_bound")
            max_radius_residual = evaluate_threshold(min_star_num=1000,count=5,case="lower_bound")

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

        return threshold_iteration

    # find the minium search radius required to find n clusters
    def solve_for_n_clusters(self, n_desired_clusters):

        # fitness function which is passed through the least squares optimiser
        def fitness_function(x):

            # try a new input, with an updated min_star_num
            self.inputs = replace(self.inputs, min_star_num=x)

            # run processing and find residual
            StarFilter(self).local_density()

            if len(self.pixels_in_clusters) > 0:
                Starfield(self).count_stars()
                residual = n_desired_clusters - self.n_clusters
            else:
                residual = 100

            # debugging information
            if __name__ == "__main__":
                print(f"Residual = {residual}, from min_star_num = {x}")

            return residual

        # read in the image
        FrameReader(self).pre_process()

        # bisection solving to determine ideal star detection threshold inside search radius
        result = bisect(fitness_function, 1, 1000)

        # return an optimum minimum star count
        return result

    # runs through the processing pipeline for a standard frame
    def process(self):
        FrameReader(self).pre_process()
        StarFilter(self).local_density()
        Starfield(self).count_stars()
        Starfield(self).register_star_properties()
        StarAlignmentVectors(self).from_biggest_star()

        return self

    # run numerical solving methods to determine the optimal min_star_number for image filtering
    def process_with_solver(self, n_desired_clusters):
        optimal_min_star_radius = self.solve_for_n_clusters(n_desired_clusters) # calls FilterImage and CatalogueClusters to do this
        Starfield(self).register_star_properties()
        StarAlignmentVectors(self).from_biggest_star()

        return optimal_min_star_radius

if __name__ == "__main__":
    data_dir = Path(r"D:\_Local\OneDrive\Astronomy\StarTrack\dev\raw_data_horsehead")
    t_val = 254
    verbosity = 1
    light = LightFrame(frame_directory=data_dir, frame_name="20210212210734 [ISO400] [60.2s] [f4.7] [288mm].NEF", verbosity=verbosity, min_star_num=20, threshold_value=225)
    light.process_with_solver(5)
    # threshold_tuned = light.tune_threshold()
    # print(f"Threshold tuned: {threshold_tuned}")