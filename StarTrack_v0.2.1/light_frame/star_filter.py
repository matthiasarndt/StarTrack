
# dependencies
import numpy as np
from PIL import Image

class StarFilter:
    def __init__(self, state):
        # separate out inputs (immutable) from state (mutable, and will be used later on in processing)
        self.state = state
        self.inputs = self.state.inputs

    def local_density(self, *args):

        # print status message
        if self.inputs.verbosity > 0: print(f"Filtering pixels, with detection radius: {self.inputs.star_detect_radius} and minimum detection count: {self.inputs.min_star_num}")

        # define empty output matrices
        self.state.pixels_in_clusters = []

        # create empty array to store pixels identified as being in clusters
        clustered_pixels_array = np.zeros(self.state.threshold_array.shape, dtype=np.uint8)

        # create star_pixels arrays
        star_pixels_yx = np.array(np.where(self.state.threshold_array == 255))
        star_pixels_y, star_pixels_x = star_pixels_yx

        # check every point, and log which pixels exceed the star detection radius
        for i_pixel in range(star_pixels_y.shape[0]):

            # define the bounds to be searched
            ref_y, ref_x = star_pixels_y[i_pixel], star_pixels_x[i_pixel]
            lower_x = ref_x - self.inputs.star_detect_radius
            upper_x = ref_x + self.inputs.star_detect_radius
            lower_y = ref_y - self.inputs.star_detect_radius
            upper_y = ref_y + self.inputs.star_detect_radius

            # check where mask overlaps and combine output into a single array
            mask_x = (star_pixels_x > lower_x) & (star_pixels_x < upper_x)
            mask_y = (star_pixels_y > lower_y) & (star_pixels_y < upper_y)
            mask_yx = mask_x & mask_y
            adjacent_star_pixels = np.vstack((star_pixels_y[mask_yx], star_pixels_x[mask_yx]))

            # we add 1 because filtered_stars will always have a minimum length of 1 (as the reference star will be in it)
            if adjacent_star_pixels.shape[1] > (self.inputs.min_star_num + 1):

                # save the pixel co-ordinates to pixels in co-ordinates list
                self.state.pixels_in_clusters.append([ref_x, ref_y])

                # add identified pixels to clustered_pixels_array
                clustered_pixels_array[ref_y][ref_x] = 255

                # print output message
                if self.inputs.verbosity > 1: print(f"Multipixel object detected at ({ref_x},{ref_y}) with {(adjacent_star_pixels.shape[1] - 1)} adjacent pixels!")


        # print output message
        if self.inputs.verbosity > 0:print(f"Filtering complete! {len(self.state.pixels_in_clusters)} pixels in clusters detected")

        # show the image is verbosity > 2
        if self.inputs.verbosity > 2:
            clustered_pixels_frame = Image.fromarray(clustered_pixels_array)
            clustered_pixels_frame.show()

        # convert to numpy array
        self.state.pixels_in_clusters = np.array(self.state.pixels_in_clusters)

        return self.state