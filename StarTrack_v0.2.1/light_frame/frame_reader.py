
# dependencies
import numpy as np
import rawpy
from PIL import Image, ImageFilter
from pathlib import Path

class FrameReader:
    def __init__(self, state):
        # separate out inputs (immutable) from state (mutable, and will be used later on in processing)
        self.state = state
        self.inputs = self.state.inputs

    def processing(self, *args):

        # convert to grayscale
        self.state.mono_frame = self.state.rgb_frame.convert('L')

        # log update to output
        if self.inputs.verbosity > 0: print(f"Loading {self.inputs.frame_directory}\\{self.inputs.frame_name}")

        # convert to numpy array for processing
        self.state.mono_array = np.array(self.state.mono_frame)

        # threshold the image
        self.state.threshold_array = (self.state.mono_array > self.inputs.threshold_value) * 255  # pixels above threshold become 255, others 0
        threshold_frame = Image.fromarray(self.state.threshold_array.astype(np.uint8))

        # blur the image
        blur_frame = threshold_frame.filter(ImageFilter.GaussianBlur(radius=self.inputs.blur_radius))
        blur_array = np.array(blur_frame)

        # re-threshold the blurred image
        self.state.threshold_array = (blur_array > 100) * 255  # pixels above threshold become 255, others 0

        # calculate the pixels to be cropped
        masked_array = np.zeros_like(self.state.threshold_array)
        crop_x = (1 - self.inputs.crop_factor) * np.shape(self.state.threshold_array)[0]
        crop_x = int(crop_x)
        crop_y = (1 - self.inputs.crop_factor) * np.shape(self.state.threshold_array)[1]
        crop_y = int(crop_y)

        # crop the image and mutate threshold array
        masked_array[crop_x:-crop_x, crop_y:-crop_y] = self.state.threshold_array[crop_x:-crop_x, crop_y:-crop_y]
        self.state.threshold_array = masked_array

        # print completion confirmation
        if self.inputs.verbosity > 0: print(f"{self.inputs.frame_name} Processing complete: monochrome, threshold and crop applied")

        # debugging information
        if self.inputs.verbosity > 1:
            threshold_frame = Image.fromarray(self.state.threshold_array.astype(np.uint8))
            threshold_frame.show()
            blur_frame.show()
            self.state.mono_frame.show()

        return self

    def pre_process(self, *args):

        # find image
        read_path = Path(self.inputs.frame_directory)/self.inputs.frame_name

        # decide on path and then import
        if read_path.suffix.lower() == ".nef":
            with rawpy.imread(str(read_path)) as raw:
                rgb_array_raw = raw.postprocess(use_camera_wb=True, output_bps=8)
            self.state.rgb_frame = Image.fromarray(rgb_array_raw)

        elif read_path.suffix.lower() in [".jpg",".jpeg",".png"]:
            self.state.rgb_frame = Image.open(read_path)

        else :
            raise TypeError("Unsupported file type")

        # once data is read, pre-process
        self.processing(self)

        return self

