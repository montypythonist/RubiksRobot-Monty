import cv2
from time import sleep
from numpy import float32
from json import load, dump
import kociemba
from collections import Counter

def clickimage(image_path): # will take a picture and make grid to scan each color
    cap = cv2.VideoCapture(0)
    sleep(2)
    ret, frame = cap.read()
    cap.release()
    if ret:
        height, width, _ = frame.shape
        square_size = min(width, height) // 5
        offset_x = (width - 3 * square_size) // 2
        offset_y = (height - 3 * square_size) // 2

        # Draw grid on the image
        for i in range(3):
            for j in range(3):
                x1, y1 = offset_x + j * square_size, offset_y + i * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Crop the image to include only the Rubik's Cube
        cropped_image = frame[offset_y:offset_y + 3 * square_size, offset_x:offset_x + 3 * square_size]
        
        # Save the cropped image
        cv2.imwrite(image_path, cropped_image)
    else:
        print("Failed to capture image.")

clickimage("~/VS-Code/RubiksRobot/faces/back.jpg")
clickimage("~/VS-Code/RubiksRobot/faces/down.jpg")
clickimage("~/VS-Code/RubiksRobot/faces/front.jpg")
clickimage("~/VS-Code/RubiksRobot/faces/left.jpg")
clickimage("~/VS-Code/RubiksRobot/faces/right.jpg")
clickimage("~/VS-Code/RubiksRobot/faces/up.jpg")

# BGR thresholds
whitemin = (100, 100, 100)
whitemax = (255, 255, 255)
redmin = (30, 30, 110)
redmax = (60, 60, 200)
orangemin = (10, 40, 100)
orangemax = (70, 100, 220)
yellowmin = (40, 100, 120)
yellowmax = (80, 170, 210)
greenmin = (30, 90, 50)
greenmax = (80, 190, 160)
bluemin = (80, 40, 20)
bluemax = (170, 100, 110)

def color_checker(BGR_tuple):
    if all(whitemin[i] <= BGR_tuple[i] <= whitemax[i] for i in range(3)):
        return "white"
    elif all(redmin[i] <= BGR_tuple[i] <= redmax[i] for i in range(3)):
        return "red"
    elif all(orangemin[i] <= BGR_tuple[i] <= orangemax[i] for i in range(3)):
        return "orange"
    elif all(yellowmin[i] <= BGR_tuple[i] <= yellowmax[i] for i in range(3)):
        return "yellow"
    elif all(greenmin[i] <= BGR_tuple[i] <= greenmax[i] for i in range(3)):
        return "green"
    elif all(bluemin[i] <= BGR_tuple[i] <= bluemax[i] for i in range(3)):
        return "blue"
    else:
        return "unknown"

def get_dominant_color(image):
    pixels = float32(image.reshape(-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, _, palette = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return tuple(map(int, palette[0]))

def color(image_path: str, cube_side: str):
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image.")
        return

    h, w, _ = img.shape
    square_height = h // 3
    square_width = w // 3

    with open('~/VS-Code/RubiksRobot/storing.json', 'r') as file:
        cube = load(file)

    for i in range(3):
        for j in range(3):
            y1 = i * square_height
            y2 = (i + 1) * square_height
            x1 = j * square_width
            x2 = (j + 1) * square_width
            square = img[y1:y2, x1:x2]
            color = get_dominant_color(square)
            color_name = color_checker(color)
            k = i * 3 + j
            cube[cube_side][k] = color_name

    with open('~/VS-Code/RubiksRobot/storing.json', 'w') as file:
        dump(cube, file, indent=4)

color("~/VS-Code/RubiksRobot/faces/back.jpg", "back")
color("~/VS-Code/RubiksRobot/faces/down.jpg", "down")
color("~/VS-Code/RubiksRobot/faces/front.jpg", "front")
color("~/VS-Code/RubiksRobot/faces/left.jpg", "left")
color("~/VS-Code/RubiksRobot/faces/right.jpg", "right")
color("~/VS-Code/RubiksRobot/faces/up.jpg", "up")

# Load cube state from JSON file
def loading(filename):
    with open(filename, 'r') as file:
        return load(file)

# Check for any unknown values
def checkunknown(cube):
    for face, stickers in cube.items():
        for i, color in enumerate(stickers):
            if color == "unknown":
                return False
    return True

# Map center stickers (which define the face) to standard notation
def facemapping(cube):
    color_to_face = {}
    # Safely map colors to faces based on the center pieces
    try:
        color_to_face[cube["up"][4]] = 'U'
        color_to_face[cube["down"][4]] = 'D'
        color_to_face[cube["front"][4]] = 'F'
        color_to_face[cube["back"][4]] = 'B'
        color_to_face[cube["left"][4]] = 'L'
        color_to_face[cube["right"][4]] = 'R'
    except IndexError:
        raise ValueError("Error: The cube state appears to be incomplete or incorrectly formatted.")
    
    return color_to_face

# Create the cube string for kociemba
def kociembastring(cube, color_to_face):
    face_order = ["up", "right", "front", "down", "left", "back"]
    cube_string = ""

    for face in face_order:
        stickers = cube[face]
        for color in stickers:
            if color not in color_to_face:
                raise ValueError(f"Color '{color}' is not mapped to a face.")
            cube_string += color_to_face[color]

    return cube_string

def validity(cube_string):
    if len(cube_string) != 54:
        print("Invalid length:", len(cube_string))
        return False

    counts = Counter(cube_string)
    print("Face counts:", counts)

    # Check that each face label appears exactly 9 times
    for face in ['U', 'D', 'F', 'B', 'L', 'R']:
        if counts[face] != 9:
            print(f"Invalid count for face '{face}': {counts[face]}")
            return False

    return True

# Solve the cube
def solution(cube):
    if not checkunknown(cube):
        print(
            "\n\n\nColors detected incorrectly!\n\n"
            "Details:\n"
            f"Correct Detection: {checkunknown(cube)}\n"
            f"Validity: {validity(cube)}\n\n\n"
        )
        return "Failed"

    color_to_face = facemapping(cube)
    cube_string = kociembastring(cube, color_to_face)

    # Now check validity after the cube string is created
    if not validity(cube_string):
        print(
            "\n\n\nColors detected incorrectly!\n\n"
            "Details:\n"
            f"Correct Detection: {checkunknown(cube)}\n"
            f"Validity: {validity(cube_string)}\n\n\n"
        )
        return "Failed"

    # Detect a truly solved cube state string and do nothing
    solved_str = 'U'*9 + 'R'*9 + 'F'*9 + 'D'*9 + 'L'*9 + 'B'*9
    #if cube_string == solved_str:
        # cube is already solved — bail out silently
        #return "Cube is already solved"

    # Otherwise solve as normal
    solution_str = kociemba.solve(cube_string)
    if not solution_str:
        return ""
    
    print("\n\n\n" + solution_str + "\n\n\n")
    return "Successful!"

cube_state = loading('~/VS-Code/RubiksRobot/storing.json')
print(type(solution(cube_state)))
print(solution(cube_state))
cube = solution(cube_state)
moves = cube.split(" ")

class clockwise:
    # CLOCKWISE MOVEMENT FUNCTIONS

    def F():
        #clockwise rotation in front
        return
    def R():
        #clockwise rotation on right
        return
    def U():
        #clockwise rotation on up
        return
    def L():
        #clockwise rotation on left
        return
    def B():
        #clockwise rotation on back
        return
    def D():
        #clockwise rotation on down
        return

class counterclockwise:
    # COUNTERCLOCKWISE MOVEMENT FUNCTIONS

    def F():
        #counterclockwise rotation in front
        return
    def R():
        #counterclockwise rotation on right
        return
    def U():
        #counterclockwise rotation on up
        return
    def L():
        #counterclockwise rotation on left
        return
    def B():
        #counterclockwise rotation on back
        return
    def D():
        #counterclockwise rotation on down
        return

class doubleclockwise:
    # DOUBLE CLOCKWISE MOVEMENT FUNCTIONS

    def F():
        #double clockwise rotation in front
        return
    def R():
        #double clockwise rotation on right
        return
    def U():
        #double clockwise rotation on up
        return
    def L():
        #double clockwise rotation on left
        return
    def B():
        #double clockwise rotation on back
        return
    def D():
        #double clockwise rotation on down
        return
moves = ""


for i in range(len(moves)):
    if moves[i] == "F":
        clockwise.F()

    elif moves[i] == "R":
        clockwise.R()

    elif moves[i] == "U":
        clockwise.U()

    elif moves[i] == "L":
        clockwise.L()
        
    elif moves[i] == "B":
        clockwise.B()
        
    elif moves[i] == "D":
        clockwise.D()

    elif moves[i] == "F\'":
        counterclockwise.F()

    elif moves[i] == "R\'":
        counterclockwise.R()

    elif moves[i] == "U\'":
        counterclockwise.U()

    elif moves[i] == "L\'":
        counterclockwise.L()

    elif moves[i] == "B\'":
        counterclockwise.B()
        
    elif moves[i] == "D\'":
        counterclockwise.D()
    
    elif moves[i] == "F2":
        doubleclockwise.F()

    elif moves[i] == "R2":
        doubleclockwise.R()

    elif moves[i] == "U2":
        doubleclockwise.U()

    elif moves[i] == "L2":
        doubleclockwise.L()
        
    elif moves[i] == "B2":
        doubleclockwise.B()
        
    elif moves[i] == "D2":
        doubleclockwise.D()