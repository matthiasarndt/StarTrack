
# dependencies
import os
from dataclasses import dataclass
import numpy as np
from pathlib import Path
from StarTrack import LightFrame, CoupledFrames
from PIL import Image

# useful functions for directory manipulation
def delete_previous_output(directory,output_list):

    # loop through each image
    for output_image in output_list:

        # if the image already exists, delete the previous output
        if output_image in os.listdir(directory): os.remove(os.path.join(directory, output_image))

def list_data_in_directory(directory):

    image_files = []
    all_files = os.listdir(directory)
    for file in all_files:
        if os.path.isfile(Path(directory, file)):
            image_files.append(file)

    return image_files

class AstroPhoto:
    # define inputs as a data class which is frozen
    @dataclass(frozen=True)
    class AstroPhotoData:
        data_directory: Path
        ref_frame_name: str = None
        verbosity: int = 0
        n_aligning_stars: int = 5
        threshold_value: int = 240
        stacking_method: str = 'mean' # to be implemented: 'sigma_clipping', 'mean_pixel_rejection','median'

    def __init__(self, **kwargs):
        # import inputs from dataclass
        self.stacked_frame = None
        self.stacked_array = None
        self.aligned_frames_stack = None
        self.inputs = self.AstroPhotoData(**kwargs)
        self.output_directory = Path(self.inputs.data_directory) / "outputs"

    def align_frames(self):

        # 1: list all images in directory, make outputs folder, and delete previous outputs
        self.output_directory.mkdir(parents=True, exist_ok=True)
        delete_previous_output(self.output_directory,output_list=["reference_frame.jpg", "stacked_frames.jpg"])
        image_list = list_data_in_directory(self.inputs.data_directory)
        print(f"Reading all image data in {self.inputs.data_directory}")

        # 2: determine index of reference frame
        if self.inputs.ref_frame_name is None:
            i_ref_frame = 0
        else:
            i_ref_frame = image_list.index(self.inputs.ref_frame_name)

        # 3: initialise main light frame
        light_ref = LightFrame(frame_directory=self.inputs.data_directory, frame_name=image_list[i_ref_frame],verbosity=self.inputs.verbosity)
        print(f"Intialising reference frame ({image_list[i_ref_frame]})")

        # 4: process with image with a solver as the search radius to find the desired number of stars is not known
        detection_threshold = light_ref.process_with_solver(n_desired_clusters=self.inputs.n_aligning_stars)
        light_ref.mono_frame.save(Path(self.output_directory) / "reference_frame.jpg")
        print(f"Star detection threshold tuned to {detection_threshold} for reference image {image_list[i_ref_frame]} to identify largest {self.inputs.n_aligning_stars} stars")

        # 5: create empty NaN to add each aligned frame to
        n_images = len(image_list)
        self.aligned_frames_stack = np.full((n_images, light_ref.mono_array.shape[0], light_ref.mono_array.shape[1]), np.nan, dtype=np.float32)
        self.aligned_frames_stack[0, :, :] = light_ref.mono_array

        # 6: remove the reference image from the image_list
        image_list.pop(i_ref_frame)

        # 7: create addition_frame_counter
        addition_frame_counter = 0

        # 8: loop through each additional frame, and process
        for i_frame in range(len(image_list)):

            # a: add a cuonter for images
            addition_frame_counter += 1

            # b: if it's the first additional frame, work out what the search parameter should be
            if addition_frame_counter == 1:

                # if it's the first addition frame, solve for the required star detection threshold
                light_addition = LightFrame(frame_directory=self.inputs.data_directory, frame_name=image_list[i_frame])
                print(f"Intialising first additional frame ({image_list[i_frame]})")

                detection_threshold = light_addition.process_with_solver(n_desired_clusters=self.inputs.n_aligning_stars*6)
                print(f"Star detection threshold tuned to {detection_threshold} for additional images {image_list[i_frame]} to identify largest {self.inputs.n_aligning_stars*6} stars")

            else:

                # after the first addition image, run with the previously determined detection_threshod
                light_addition = LightFrame(frame_directory=self.inputs.data_directory, frame_name=image_list[i_frame],min_star_num=detection_threshold)
                light_addition.process()

            # c: create object which couples the reference and additonal light
            lights_paired = CoupledFrames(light_ref, light_addition)

            # d: align the additional frame with the reference frame
            lights_paired.align()
            print(f"Aligned image {light_addition.inputs.frame_name} with {light_ref.inputs.frame_name}")

            # e: store the resulting aligned image into the output array below
            self.aligned_frames_stack[(i_frame + 1), :, :] = lights_paired.addition_frame_aligned

        return self

    def stack_aligned_frames(self):

        # delete previous stacked image
        delete_previous_output(self.output_directory,output_list=['stacked_frame.jpg'])

        if self.inputs.stacking_method == 'mean':
            # choose averaging method depending on inputs - currently only one implemented
            self.stacked_array = np.mean(self.aligned_frames_stack, axis=0)

        # convert the image to an array, making sure to make it 8 bit
        self.stacked_frame = Image.fromarray(self.stacked_array.astype(np.uint8))
        self.stacked_frame.show()
        self.stacked_frame.save(Path(self.output_directory) / "stacked_frame.jpg")

        return self

if __name__ == "__main__":
    iris_nebula = AstroPhoto(data_directory=Path('D:\_Local\OneDrive\Astro\AstroCode\Data2'))
    iris_nebula.align_frames()
    iris_nebula.stack_aligned_frames()