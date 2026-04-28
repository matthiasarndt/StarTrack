# Roadmap

### Version 0.3 
The main focus for V0.3 is the introduction of the PostProcessor module, which was introduced with 0.3.0. In addition to this, there are general docstring improvements, some structural changes, and the introduction of a configuration database to store important variables required between modules. 

#### Version 0.3.5
Integration of the stacking_algorithm.py module into the code, with only the "mean" method fully integrated for now. More methods (median, sigma-gamma, weighted average, iterative methods) will be integrated during the frame_stack refactor in Version 0.5. See below. 

### Version 0.4
The main focus for V0.4 is the introduction of a denoiser module, built using PyTorch with a CNN architecture. This will have the following modules:
* dataset.py - to translate the stack/stacked image into noisy and clean data for training, testing, and validation.
* model.py - to architect the model.
* train.py - to train the model.
* inference.py - to run the model on all noisy input frames. The cleaned input data will then be re-stacked and processed. 

### Version 0.5
The main focus of V0.5 is to re-architect the frame_stack module, improving performance and restructuring the code. The current frame_stack module has grown far beyond it's initial scope - the plan is to break it down into smaller modules, with a focus on registration and alignment of frames into the memory mapped array, stacking, and a stack module to act as a dataclass and handle memory mapping operations. This will be a major restructure and improvement to the codebase - which is why it will be a major rather than a minor patch. 

