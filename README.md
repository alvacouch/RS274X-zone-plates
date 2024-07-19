# RS274X-zone-plates
Code to generate zone plates and pinhole sieves

Version pre-alpha: not intended for public reuse as yet. 

# Structure
* job1 -- the first job sent to Fineline-Imaging.com with all documentation. 
* job2 -- the second print job sent to Fineline-Imaging.com with only the source code and output. 
* experimental -- things I'm playing with that haven't been sent to Fineline-Imaging.com for printing
  * Probabilistic -- a 100mm probabilistic zone plate generator. 
  * 2000mm -- a 2000mm classic zone plate for a telescope. 

# Usage
These scripts are designed to run within the distribution direectory for GLIF (https://github.com/python50/GLIF). This is a tool suite that is an extension of 
pcb-tools (https://pypi.org/project/pcb-tools/) and contains a complete copy of same at an earlier version. The main purpose of GLIF is to generate text output as part of the printer input. 

TO use one of the scripts, clone GLIF, copy the script into the GLIF directory, and then run it with a version of Python 3. 

