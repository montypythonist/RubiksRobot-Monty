# RubiksRobot-Monty (ALPHA STAGE)
camera-based rubik's cube solver for raspberry pi, read this repo's wiki for more info on how to use

## program walkthrough:

- `faces/` stores the initial images of the Rubik's Cube by each side

- `clickimage.sh` is the program that takes the images of the Rubik's Cube, stores them in `faces/`, then automatically starts running `rubiksrobot-monty.py`. 
     - we would have used OpenCV to take the image and just have `rubiksrobot-monty.py` be the only running program, but there were limitations to this on the Pi 4.
 
- `storing.json` stores detected colors 

- `rubiksrobot-monty.py` is the actual program that crops and edits the images in `faces/`, runs color detections and stores the detected colors in `storing.json`, then spits out an algorithm to solve the Rubik's Cube based off of what is in `storing.json`