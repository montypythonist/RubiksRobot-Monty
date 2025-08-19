# RubiksRobot-Monty (ALPHA STAGE)
camera-based rubik's cube solver (stale branch for mac/windows), read this repo's wiki for more info on how to use

## program walkthrough:

- `faces/` stores the initial images of the Rubik's Cube by each side
 
- `storing.json` stores detected colors 

- `rubiksrobot-monty.py` is the actual program that takes, crops, and edits the images in `faces/`, runs color detections and stores the detected colors in `storing.json`, then spits out an algorithm to solve the Rubik's Cube based off of what is in `storing.json`