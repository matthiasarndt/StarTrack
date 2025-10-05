
# dependencies
import os
import gc
import traceback
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from collections import namedtuple
from pathlib import Path
from StarTrack import LightFrame, CoupledFrames
from PIL import Image

### useful functions for directory manipulation ###
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

###  worker functions required for parallelisation ###
def worker_process_with_solver(solver_initialisation_args):

    solve_frame = solver_initialisation_args.frame

    print(f"Processing Frame: {solve_frame.inputs.frame_name}")
    solve_frame.process_with_solver(n_desired_clusters=solver_initialisation_args.n_desired_stars)

    return solve_frame

def align_single_frame(i_layer, light_ref, light_addition):

    # create object which couples the reference and additonal light
    lights_paired = CoupledFrames(light_ref, light_addition)

    # align the additional frame with the reference frame
    lights_paired.align()
    print(f"Aligned image {light_addition.inputs.frame_name} with {light_ref.inputs.frame_name}")

    # store the resulting aligned image into the output array below
    return i_layer, lights_paired.addition_frame_aligned

def add_frames_worker(arg_tuple):

    # try/catch to keep the pool running if there are errors with any individual frames
    try:

        # define and process addition frame
        frame_add = LightFrame(frame_directory=arg_tuple.data_dir,frame_name=arg_tuple.image_name,min_star_num=arg_tuple.detect_threshold)
        frame_add.process()

        # memory crashes occur if a memory cleanup is not performed as each frame is processed
        gc.collect()

        # align the frame
        i_layer, aligned_array = align_single_frame(arg_tuple.i_layer, arg_tuple.light_ref, frame_add)

        # create a dict to return a successful results:
        return {"i_layer": i_layer,"aligned_array": aligned_array}

    except Exception as e:

        # generate diagnostics error dict
        return {"error": str(e),"traceback": traceback.format_exc(),"i_layer": getattr(arg_tuple, "i_layer", None),"image_name": getattr(arg_tuple, "image_name", None)}


### named tuple required for parallelisation of workers ###
SolverInitialisationFrames = namedtuple("SolverInitialisationFrames",["frame","n_desired_stars"])
AdditionalFrames = namedtuple("AdditionalFrames",["i_layer", "image_name", "data_dir", "detect_threshold", "light_ref"])

### class definition for AstroPhoto ###
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
        max_cores: int = 5

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
        delete_previous_output(self.output_directory, output_list=["reference_frame.jpg", "stacked_frames.jpg"])
        image_list = list_data_in_directory(self.inputs.data_directory)
        print(f"Reading all image data in {self.inputs.data_directory}")

        # 2: determine index of reference frame:
        if self.inputs.ref_frame_name is None:
            i_ref_frame = 0
        else:
            i_ref_frame = image_list.index(self.inputs.ref_frame_name)

        # 3: create reference frame object
        light_ref = LightFrame(frame_directory=self.inputs.data_directory, frame_name=image_list[i_ref_frame],
                               verbosity=self.inputs.verbosity)

        # 4: remove the reference image from the image_list
        image_list.pop(i_ref_frame)

        # 5: create first additonal frame object
        light_addition = LightFrame(frame_directory=self.inputs.data_directory, frame_name=image_list[0])

        # 6: solve both frames in parallel:
        print(f"Intialising Reference Frame: ({light_ref.inputs.frame_name})")
        print(f"Intialising First Additional Frame: ({light_addition.inputs.frame_name})")
        ref_frame_args = SolverInitialisationFrames(light_ref,self.inputs.n_aligning_stars)
        first_add_frame_args = SolverInitialisationFrames(light_addition,self.inputs.n_aligning_stars*6)
        with ProcessPoolExecutor(max_workers=2) as executor:
            light_ref, light_addition = executor.map(worker_process_with_solver, [ref_frame_args, first_add_frame_args])

        # 7: save solving paramters, reference frame image, & print to terminal
        light_ref.mono_frame.save(Path(self.output_directory) / "reference_frame.jpg")
        ref_detect_threshold = light_ref.inputs.min_star_num
        add_detect_threshold = light_addition.inputs.min_star_num
        print(f"Star detection radius tuned to {ref_detect_threshold} for reference image {light_ref.inputs.frame_name} to identify largest {self.inputs.n_aligning_stars} stars")
        print(f"Star detection radius tuned to {add_detect_threshold} for additional images {image_list[0]} to identify largest {self.inputs.n_aligning_stars * 6} stars")

        # clean-up memory as the initialisation process is complete
        gc.collect()

        # 8: create empty NaN to add each aligned frame to
        n_images = len(image_list) + 1 # the reference image has been removed from the image_list, so need to add + 1
        self.aligned_frames_stack = np.full((n_images, light_ref.mono_array.shape[0],light_ref.mono_array.shape[1]),np.nan, dtype=np.float32)
        self.aligned_frames_stack[0, :, :] = light_ref.mono_array
        self.aligned_frames_stack[1, :, :] = light_addition.mono_array

        # 9: define inputs for the remainder of frames to be processed, with a named tuple as input structure and list comprehension
        args_tuple = [AdditionalFrames(i_layer, image_list[i_layer], self.inputs.data_directory, add_detect_threshold, light_ref)
            for i_layer in range(1, len(image_list))]

        # 10: execute the processing of all remaining frames in parallel
        with ProcessPoolExecutor(max_workers=self.inputs.max_cores) as executor:

            # wrap each process in try/except so that errors won't crash the pool. this has been implemented with multiprocessing futures
            futures = [executor.submit(add_frames_worker, args) for args in args_tuple]
            for future in as_completed(futures):
                result = future.result()
                if "error" in result:
                    print(f"Aligment Failure: {result['image_name']}")
                    continue  # skip this frame
                self.aligned_frames_stack[result["i_layer"] + 1, :, :] = result["aligned_array"]

        # 11: remove any layers that have NaNs in them (meaning an unsuccessful frame alignment - see step 11)
        self.aligned_frames_stack = self.aligned_frames_stack[~np.all(np.isnan(self.aligned_frames_stack), axis=(1, 2))]

    def stack_aligned_frames(self):

        # delete previous stacked image
        delete_previous_output(self.output_directory,output_list=['stacked_frame.jpg'])

        # choose averaging method depending on inputs - currently only one implemented
        if self.inputs.stacking_method == 'mean':
            self.stacked_array = np.mean(self.aligned_frames_stack, axis=0)

        # convert the image to an array, making sure to make it 8 bit
        self.stacked_frame = Image.fromarray(self.stacked_array.astype(np.uint8))
        self.stacked_frame.show()
        self.stacked_frame.save(Path(self.output_directory) / "stacked_frame.jpg")

        return self