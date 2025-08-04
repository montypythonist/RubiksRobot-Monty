#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rpicam-still -o "$SCRIPT_DIR/faces/back.jpg"
rpicam-still -o "$SCRIPT_DIR/faces/down.jpg"
rpicam-still -o "$SCRIPT_DIR/faces/front.jpg"
rpicam-still -o "$SCRIPT_DIR/faces/left.jpg"
rpicam-still -o "$SCRIPT_DIR/faces/right.jpg"
rpicam-still -o "$SCRIPT_DIR/faces/up.jpg"
/usr/bin/python3 "$SCRIPT_DIR/rubiksrobot-monty.py"