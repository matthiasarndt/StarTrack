
# dependencies
import numpy as np

class Utils:

    @staticmethod
    def local_density_filter(search_array, star_detect_radius, star_detect_pixels):

        # create empty array to store pixels identified as being in clusters
        output_array = np.zeros(search_array.shape, dtype=np.uint8)

        # create star_pixels arrays
        star_pixels_yx = np.array(np.where(search_array == 255))
        star_pixels_y, star_pixels_x = star_pixels_yx

        # check every point, and log which pixels exceed the star detection radius
        for i_pixel in range(star_pixels_y.shape[0]):

            # define the bounds to be searched
            ref_y, ref_x = star_pixels_y[i_pixel], star_pixels_x[i_pixel]
            lower_x = ref_x - star_detect_radius
            upper_x = ref_x + star_detect_radius
            lower_y = ref_y - star_detect_radius
            upper_y = ref_y + star_detect_radius

            # check where mask overlaps and combine output into a single array
            mask_x = (star_pixels_x > lower_x) & (star_pixels_x < upper_x)
            mask_y = (star_pixels_y > lower_y) & (star_pixels_y < upper_y)
            mask_yx = mask_x & mask_y
            adjacent_star_pixels = np.vstack((star_pixels_y[mask_yx], star_pixels_x[mask_yx]))

            # we add 1 because filtered_stars will always have a minimum length of 1 (as the reference star will be in it)
            if adjacent_star_pixels.shape[1] > (star_detect_pixels + 1):
                # save the pixel co-ordinates to pixels in co-ordinates list
                # self.state.pixels_in_clusters.append([ref_x, ref_y])

                # add identified pixels to output_array
                output_array[ref_y][ref_x] = 255

        return output_array