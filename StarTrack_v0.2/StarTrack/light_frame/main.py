
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

    # find the minium search radius required to find n clusters
    def solve_for_n_clusters(self, n_desired_clusters):

        # print update message
        print(f"Assessing image star density to solve for detection threshold required to find {n_desired_clusters} largest stars")

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
        Starfield(self).catalogue_properties()
        StarAlignmentVectors(self).from_biggest_star()

        return self

    # run numerical solving methods to determine the optimal min_star_number for image filtering
    def process_with_solver(self, n_desired_clusters):
        optimal_min_star_radius = self.solve_for_n_clusters(n_desired_clusters) # calls FilterImage and CatalogueClusters to do this
        Starfield(self).catalogue_properties()
        StarAlignmentVectors(self).from_biggest_star()

        return optimal_min_star_radius

if __name__ == "__main__":
    data_dir = Path(r"C:\")
    light = LightFrame(frame_directory=data_dir, frame_name="L_0168.jpg",verbosity=1,min_star_num = 10)
    light.process()
