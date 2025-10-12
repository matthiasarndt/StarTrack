
# dependencies
import os
import gc
import traceback
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, replace
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
def worker_process_with_tuning(solver_initialisation_args):

    solve_frame = solver_initialisation_args.frame
    solve_frame.process_tuning_star_detect(n_desired_clusters=solver_initialisation_args.n_desired_stars)

    return solve_frame

def align_single_frame(i_layer, light_ref, light_addition):

    # create object which couples the reference and additonal light
    lights_paired = CoupledFrames(light_ref, light_addition)

    # align the additional frame with the reference frame
    lights_paired.align()
    print(f"Aligned image {light_addition.inputs.frame_name} with {light_ref.inputs.frame_name}")

    # store the resulting aligned image into the output array below
    return i_layer, lights_paired.addition_aligned_array_mono, lights_paired.addition_aligned_array_r, lights_paired.addition_aligned_array_g, lights_paired.addition_aligned_array_b

def add_frames_worker(arg_tuple):

    # try/catch to keep the pool running if there are errors with any individual frames
    try:

        # define and process addition frame
        frame_add = LightFrame(frame_directory=arg_tuple.data_dir,frame_name=arg_tuple.image_name,star_detect_pixels=arg_tuple.detect_threshold,threshold=arg_tuple.threshold)
        frame_add.process()

        # memory crashes occur if a memory cleanup is not performed as each frame is processed
        gc.collect()

        # align the frame
        i_layer, aligned_array, aligned_array_r, aligned_array_g, aligned_array_b = align_single_frame(arg_tuple.i_layer, arg_tuple.light_ref, frame_add)

        # create a dict to return a successful results:
        return {"i_layer": i_layer,"mono": aligned_array, "r": aligned_array_r, "g": aligned_array_g, "b": aligned_array_b}

    except Exception as e:

        # generate diagnostics error dict
        return {"error": str(e),"traceback": traceback.format_exc(),"i_layer": getattr(arg_tuple, "i_layer", None),"image_name": getattr(arg_tuple, "image_name", None)}

### named tuple required for parallelisation of workers ###
SolverInitialisationFrames = namedtuple("SolverInitialisationFrames",["frame","n_desired_stars"])
AdditionalFrames = namedtuple("AdditionalFrames",["i_layer", "image_name", "data_dir", "detect_threshold", "light_ref", "threshold"])

### class definition for AstroPhoto ###
class AstroPhoto:

    # define inputs as a data class which is frozen
    @dataclass(frozen=True)
    class AstroPhotoData:

        data_directory: Path
        ref_frame_name: str = None
        verbosity: int = 0
        n_aligning_stars: int = 5
        threshold: int = 240
        stacking_method: str = 'mean' # to be implemented: 'sigma_clipping', 'mean_pixel_rejection','median'
        max_cores: int = 5

    def __init__(self, **kwargs):

        # import inputs from dataclass
        self.image_list = None
        self.ref_star_detect_pixels = None
        self.add_star_detect_pixels = None
        self.stacked_frame_mono = None
        self.stacked_frame_rgb = None
        self.stacked_array_mono = None
        self.stacked_array_r = None
        self.stacked_array_g = None
        self.stacked_array_b = None
        self.stack_mono_arrays = None
        self.stack_r_arrays = None
        self.stack_g_arrays = None
        self.stack_b_arrays = None
        self.inputs = self.AstroPhotoData(**kwargs)
        self.output_directory = Path(self.inputs.data_directory) / "outputs"

    def initialise(self):

        # list all images in directory, make outputs folder, and delete previous outputs
        self.output_directory.mkdir(parents=True, exist_ok=True)
        delete_previous_output(self.output_directory, output_list=["reference_frame_mono.jpg","reference_frame_rgb.jpg","stacked_frames_mono.jpg","stacked_frames_rgb.jpg"])
        self.image_list = list_data_in_directory(self.inputs.data_directory)

        print(f"Index image data in {self.inputs.data_directory}")

        # determine index of reference frame:
        if self.inputs.ref_frame_name is None:
            i_ref_frame = 0
        else:
            i_ref_frame = self.image_list.index(self.inputs.ref_frame_name)

        print(f"Initialising with reference frame {self.inputs.ref_frame_name}")

        # tune threshold with light_tuning instance of LightFrame. delete once generated, to reduce memory usage
        if self.inputs.threshold == -1:
            light_tuning = LightFrame(frame_directory=self.inputs.data_directory,
                                      frame_name=self.image_list[i_ref_frame],
                                      verbosity=0)
            tuned_threshold = light_tuning.tune_threshold()
            self.inputs = replace(self.inputs,threshold=tuned_threshold,verbosity=self.inputs.verbosity)
            del light_tuning
            print(f"Threshold set to -1, tuning threshold parameter")

        # create reference light frame instance
        light_tuning = LightFrame(frame_directory=self.inputs.data_directory,
                               frame_name=self.image_list[i_ref_frame],
                               verbosity=self.inputs.verbosity,
                               threshold=self.inputs.threshold)

        # tune star_detect_parameter:
        add_tuning_multiplier = 6
        ref_frame_args = SolverInitialisationFrames(light_tuning,self.inputs.n_aligning_stars)
        add_frame_args = SolverInitialisationFrames(light_tuning,self.inputs.n_aligning_stars*add_tuning_multiplier)
        with ProcessPoolExecutor(max_workers=2) as executor:
            light_tuned_ref, light_tuned_add = executor.map(worker_process_with_tuning, [ref_frame_args, add_frame_args])

        self.ref_star_detect_pixels = light_tuned_ref.inputs.star_detect_pixels
        self.add_star_detect_pixels = light_tuned_add.inputs.star_detect_pixels

        # create output matrices
        self.stack_mono_arrays = np.full((len(self.image_list), light_tuned_ref.mono_array.shape[0], light_tuned_ref.mono_array.shape[1]), 0, dtype=np.uint8)
        self.stack_r_arrays = np.full((len(self.image_list), light_tuned_ref.mono_array.shape[0], light_tuned_ref.mono_array.shape[1]), 0, dtype=np.uint8)
        self.stack_g_arrays = np.full((len(self.image_list), light_tuned_ref.mono_array.shape[0], light_tuned_ref.mono_array.shape[1]), 0, dtype=np.uint8)
        self.stack_b_arrays = np.full((len(self.image_list), light_tuned_ref.mono_array.shape[0], light_tuned_ref.mono_array.shape[1]), 0, dtype=np.uint8)

        # remove the reference image from the image_list
        self.image_list.pop(i_ref_frame)

        # 8: save solving paramters, reference frame image, & print to terminal
        light_tuned_ref.mono_frame.save(Path(self.output_directory) / "reference_frame_mono.jpg")
        light_tuned_ref.rgb_frame.save(Path(self.output_directory) / "reference_frame_rgb.jpg")

        print(f"Star detection pixels tuned to {self.ref_star_detect_pixels} for reference frame")
        print(f"Star detection pixels tuned to {self.add_star_detect_pixels} for additional frames")

        # clean-up memory as the initialisation process is complete
        gc.collect()

        test = 5

        return self

    def align_frames(self):

        # create reference light frame instance
        light_ref = LightFrame(frame_directory=self.inputs.data_directory,frame_name=self.inputs.ref_frame_name,verbosity=self.inputs.verbosity,
                                  threshold=self.inputs.threshold,star_detect_pixels=self.ref_star_detect_pixels)
        light_ref.process()

        # store light_ref mono & r/g/b data
        self.stack_mono_arrays[0, :, :] = light_ref.mono_array
        self.stack_r_arrays[0, :, :] = light_ref.r_array
        self.stack_g_arrays[0, :, :] = light_ref.g_array
        self.stack_b_arrays[0, :, :] = light_ref.b_array

        # define inputs for the remainder of frames to be processed, with a named tuple as input structure and list comprehension
        args_tuple = [AdditionalFrames(i_layer, self.image_list[i_layer], self.inputs.data_directory, self.add_star_detect_pixels, light_ref, self.inputs.threshold)
            for i_layer in range(0, len(self.image_list))]

        # execute the processing of all remaining frames in parallel
        with ProcessPoolExecutor(max_workers=self.inputs.max_cores) as executor:

            # wrap each process in try/except so that errors won't crash the pool. this has been implemented with multiprocessing futures
            futures = [executor.submit(add_frames_worker, args) for args in args_tuple]

            for future in as_completed(futures):
                result = future.result()
                if "error" in result:
                    print(f"Failed to align {result['image_name']}")
                    continue  # skip this fram

                # store aligned r/g/b data
                self.stack_mono_arrays[result["i_layer"] + 1, :, :] = result["mono"]
                self.stack_r_arrays[result["i_layer"] + 1, :, :] = result["r"]
                self.stack_g_arrays[result["i_layer"] + 1, :, :] = result["g"]
                self.stack_b_arrays[result["i_layer"] + 1, :, :] = result["b"]

        # remove any layers that have only 0s in them (indicating an unsuccessful frame alignment)
        self.stack_mono_arrays = self.stack_mono_arrays[~np.all(self.stack_mono_arrays==0,axis=(1,2))]
        self.stack_r_arrays = self.stack_r_arrays[~np.all(self.stack_r_arrays==0,axis=(1,2))]
        self.stack_g_arrays = self.stack_g_arrays[~np.all(self.stack_g_arrays==0,axis=(1,2))]
        self.stack_b_arrays = self.stack_b_arrays[~np.all(self.stack_b_arrays==0,axis=(1,2))]
        gc.collect()

    def stack_aligned_frames(self):

        # delete previous stacked image
        delete_previous_output(self.output_directory,output_list=['stacked_frame.jpg'])

        # choose averaging method depending on inputs - currently only one implemented
        if self.inputs.stacking_method == 'mean':
            self.stacked_array_mono = np.mean(self.stack_mono_arrays,axis=0)
            self.stacked_array_r = np.mean(self.stack_r_arrays,axis=0)
            self.stacked_array_g = np.mean(self.stack_g_arrays,axis=0)
            self.stacked_array_b = np.mean(self.stack_b_arrays,axis=0)

        # convert the image to an array, making sure to make it 8 bit
        stacked_frame_mono = Image.fromarray(self.stacked_array_mono.astype(np.uint8))
        stacked_frame_r = Image.fromarray(self.stacked_array_r.astype(np.uint8))
        stacked_frame_g = Image.fromarray(self.stacked_array_g.astype(np.uint8))
        stacked_frame_b = Image.fromarray(self.stacked_array_b.astype(np.uint8))

        # save mono image
        stacked_frame_mono.save(Path(self.output_directory) / "stacked_frame_mono.jpg")

        # save rgb image
        stacked_frame_rgb = Image.merge('RGB', (stacked_frame_r,stacked_frame_g,stacked_frame_b))
        stacked_frame_rgb.show()
        stacked_frame_rgb.save(Path(self.output_directory) / "stacked_frame_rgb.jpg")

        return self