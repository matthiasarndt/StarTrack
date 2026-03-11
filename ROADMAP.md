# Roadmap

### Version 0.3 
The main focus for V0.3 is the introduction of the PostProcessor module, which was introduced with 0.3.0. In addition to this, there are general docstring improvements, some structural changes, and the introduction of a configuration database to store important variables required between modules. 

#### Version 0.3.3
* Improved colour calibration module, using cumulative distribution function matching to align RGB channels. The current approach works well for aligning R/G to B (dominant when light pollution is heavy), but does not extend well to R channel.
* Improved background neutralisation by improving least squares 2D curve fitting of lens distortions to take into account linear gradients caused by light pollution. 
* Built-in visualisation functionality of histograms. 

#### Version 0.3.4
* Introduction of central config/database module inside the top level common folder.
* This will better link together source of information, e.g. dimensions of stack, tuned parameters, which are already stored in JSON files (stack parameter saving was introduced in 0.3.1).

### Version 0.4
The main focus for V0.4 is the introduction of a denoiser module, built using PyTorch with a CNN architecture. This will have the following modules:
* dataset.py - to translate the stack/stacked image into noisy and clean data for training, testing, and validation.
* model.py - to architect the model.
* train.py - to train the model.
* inference.py - to run the model on all noisy input frames. The cleaned input data will then be re-stacked and processed. 

### Version 0.5
The main focus of V0.5 is to re-architect the frame_stack module, improving performance and restructuring the code. 
