
# dependencies
import numpy as np

class StarAlignmentVectors:
    def __init__(self, state):
        self.state = state
        self.inputs = self.state.inputs

    def from_biggest_star(self):

        # find the biggest star and run from it
        self.from_index_star(i_star = np.argmax(self.state.magnitude_list, axis=0))

    def from_index_star(self, i_star):

        # find the biggest star
        self.state.i_ref_star = i_star

        # calculation of reference star, end points for vectors, and the delta between them
        self.state.ref_star = self.state.centroid_list[self.state.i_ref_star, :]
        self.state.non_ref_stars = np.copy(self.state.centroid_list)
        self.state.non_ref_stars = np.delete(self.state.non_ref_stars, self.state.i_ref_star, axis=0)
        delta = self.state.non_ref_stars - self.state.ref_star

        # calculation of angles and vectors
        self.state.ref_vectors = np.linalg.norm(delta, axis=1)
        self.state.ref_angles = np.arctan2(delta[:, 1], delta[:, 0])

        # output messages
        if self.inputs.verbosity > 0:
            print(f"Reference star position: {self.state.ref_star}")
            print(f"Reference star magnitude: {self.state.magnitude_list[self.state.i_ref_star]}")
            print(f"Vectors from reference star (index {self.state.i_ref_star} in star_centroid_list):")
            print(self.state.ref_vectors)
            print(f"Angles from reference star (index {self.state.i_ref_star} in star_centroid_list):")
            print(self.state.ref_angles)

        return self