
# dependencies
import os
from pathlib import Path
from StarTrack import AstroPhoto

# determine inputs
run_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = Path(run_dir) / "raw_data_iris_nebula"
n_aligning_stars = 5 # recommended to be 5, maximum value is 9
t_value = 252 # manually set this based on the brightness of the starfield. future 

# verbosity = 0: minimal information, tracking overall status
# verbosity = 1: figures of identified stars
# verbosity = 2: debugging information [not all information is printed, some debugging is found by individually running relevant scripts]

# create iris nebula object from astro photo, and declare variables of interest
image = AstroPhoto(data_directory=data_dir, n_aligning_stars=n_aligning_stars,verbosity=0,ref_frame_name="iris_nebula_frame_1.jpg",threshold_value=t_value)

# process iris nebula to get results!
image.align_frames()
image.stack_aligned_frames()