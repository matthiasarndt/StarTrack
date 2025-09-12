
# dependencies
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from skimage.transform import estimate_transform, warp
from StarTrack import LightFrame
from StarTrack.light_frame.star_alignment_vectors import StarAlignmentVectors

class CoupledFrames:
    def __init__(self, ref_frame, align_frame, *args):
        self.ref_frame = ref_frame
        self.addition_frame = align_frame
        self.coords_ref = None
        self.angles_ref = None
        self.coords_addition = None
        self.angles_addition = None
        self.addition_frame_aligned = None

    # determine the aligning stars for the addition frame
    def addition_aligning_stars(self):

        # sort potential reference stars in order from largest to smallest. the larger the star, the more likely it is to be the reference star
        sorted_indices = np.argsort(self.addition_frame.magnitude_list)[::-1]

        # analyse each star in turn
        for i_star in sorted_indices:

            # calculate star alignment vectors from the index star
            StarAlignmentVectors(self.addition_frame).from_index_star(i_star)

            # try to determine addition co-ordinates and angles based on the reference star guess above. If it doesn't work, it means the guess star is not the reference star
            try:
                self.coords_addition, self.angles_addition = self.calculate_aligning_stars(self.ref_frame, self.addition_frame)

                # debugging information
                if __name__ == '__main__':
                    print("Successful Star Alignment, with the Following Stars: ")
                    print(len(self.coords_addition))
                break

            # if the above code doesn't work, it will return an IndexError, as it will be searching an empty array (see the static method below)
            except IndexError:

                # debugging information
                if __name__ == '__main__':
                    print("Alignment failed, retrying...")

        return self

    # the same code is used here as in the additional aligning stars to avoid duplication
    # future releases will optimise this code
    def ref_aligning_stars(self):

        self.coords_ref, self.angles_ref = self.calculate_aligning_stars(self.ref_frame, self.ref_frame)

        return self

    def align_addition_frame(self):

        if __name__ == '__main__':
            print("Reference Alignment Co-ordinates: ")
            print(self.coords_ref)
            print("Reference Alignment Angles: ")
            print(self.angles_ref)
            print("Addition Alignment Co-ordinates: ")
            print(self.coords_addition)
            print("Addition Alignment Angles: ")
            print(self.angles_addition)

        # estimate transform matrices for "affine" image distortion assumption, using the coordinates calculated
        tform = estimate_transform('affine', self.coords_addition, self.coords_ref)

        # apply warp with inverse transform
        aligned = warp(self.addition_frame.mono_array, inverse_map=tform.inverse,
                       output_shape=self.addition_frame.mono_array.shape, preserve_range=True)

        # convert to 8 bit
        self.addition_frame_aligned = np.clip(aligned, 0, 255).astype(np.uint8)

        return self

    def align(self):
        self.addition_aligning_stars()
        self.ref_aligning_stars()
        self.align_addition_frame()

    # static method to calculate aligning stars for any two frames
    @staticmethod
    def calculate_aligning_stars(frame_main, frame_addition):

        def filter_coords(i_filter_star):

            # determine tolerance for determining the aligning stars
            tol = 0.01

            filter_angle = frame_main.ref_angles[i_filter_star]
            i_ref_angle_list = np.where(np.abs(frame_addition.ref_angles - filter_angle) < tol)[0]

            if len(i_ref_angle_list) == 1:
                i_ref_angle = i_ref_angle_list[0]

                # debugging information
                if __name__ == '__main__':
                    print(f"Identified Alignment Star Reference Indices: {i_ref_angle_list}")

            else: # it means that multiple stars are within the search angle. to isolate the correct alignment star, a further search is done on radius
                filter_distance = frame_main.ref_vectors[i_filter_star]
                i_ref_distance_list = np.where(np.abs(frame_addition.ref_vectors - filter_distance) < 1000*tol)[0] # tolerance scaled to account for order of magnitude difference between radiance and pixel distance
                i_ref_angle = np.intersect1d(i_ref_angle_list, i_ref_distance_list)[0]

                # debugging information
                if __name__ == '__main__':
                    print("Distance Check Needed")
                    print(f"Target Distance: {filter_distance}")
                    print(f"Reference Vector Distance: {frame_addition.ref_vectors}")
                    print(i_ref_distance_list)

            # co-ordinates of non-reference stars flagged by the indices above are extracted
            non_ref_stars = frame_addition.non_ref_stars[i_ref_angle, :]
            # the indices in the main array of star centroids is found here, based on the exact star co-ordinates provided above
            i_alignment_star = np.where(frame_addition.centroid_list == non_ref_stars)[0][0]

            # extract the exact co-ordinate and angle of this alignment star
            coord = frame_addition.centroid_list[i_alignment_star]
            angle = frame_addition.ref_angles[i_ref_angle]

            return coord, angle

        # calculate how many alignment stars are required and create empty output lists
        n_alignments_stars = len(frame_main.centroid_list)
        add_align_coords_list = []
        add_align_angles_list = []

        # filter star co-ordinates store properties of identified aligning stars in the reference frame
        for i_star in range(n_alignments_stars-1): # run through stars up until n_alignment - 1, because the reference alignment star is already known, and the rest need to be processed
            add_align_star_coord, add_align_star_angle = filter_coords(i_star)
            add_align_coords_list.append(add_align_star_coord)
            add_align_angles_list.append(add_align_star_angle)

        # add reference star details
        add_align_coords_list.append(frame_addition.centroid_list[frame_addition.i_ref_star])
        add_align_angles_list.append(int(0))

        # convert add_align_angles_array to numpy array
        add_align_angles_array = np.array(add_align_angles_list)

        # sort both arrays so that they match, in the order of angle from reference star
        sort_indices = np.argsort(add_align_angles_array)[::-1]
        sorted_add_align_angles_array = np.array(add_align_angles_list)[sort_indices]
        sorted_add_align_coords_array = np.array(add_align_coords_list)[sort_indices]

        return sorted_add_align_coords_array, sorted_add_align_angles_array

if __name__ == '__main__':

    # define data path
    data_dir = Path(r"C:\")
    verbosity = 0

    # create reference frame object - 157.09375
    frame_ref = LightFrame(frame_directory=data_dir, frame_name="L_0168.jpg", verbosity=verbosity, min_star_num=157.09375)
    frame_ref.process()

    # create addition frame object
    frame_add = LightFrame(frame_directory=data_dir, frame_name="L_0172.jpg", verbosity=verbosity, min_star_num = 50)
    frame_add.process()

    # couple frames and find aligning stars for reference frame
    coupled_frames = CoupledFrames(frame_ref, frame_add)
    coupled_frames.align()

    # show alignment of additional frame to reference frame
    plt.imshow(coupled_frames.addition_frame_aligned, cmap='gray')
    plt.show()
