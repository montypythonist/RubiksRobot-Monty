#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rpicam-still -o "$SCRIPT_DIR/rubiks_cube.jpg"
/usr/bin/python3 "$SCRIPT_DIR/rubiksrobot-monty.py"