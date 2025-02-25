# ProbabilityBasedEventLogGenerator
Code related to the implementation of the paper ''An Experimental Comparison of Alternative Methods for Event-Log Augmentation''

The code has been developed and tested on Both Windows 11 and Linux 24.04 LTS. With a Python 3.10.2 environment. All the simulations were executed on a workstation equipped with a 12th Gen Intel Core i7 processor and 32 GB RAM. 

# How to run the code

Create a virtual Python 3.10.2 environment and install the requirements running:

pip install -r requirements.txt

Create a folder for each alternative technique, and fill it with the experiments from "https://zenodo.org/records/5734443" and "https://drive.google.com/drive/folders/1gmO8ULxtBxqShXnBeEUhBLOy97KYlVI2", and running the publicy available code from other apporaches.

change the path to the original log in the script run_simulation.py,and run it using 

python3 run_simulation.py

Use the python notebook "LogDistanceMeasuresSim.ipynb" for testing and producing the measures.