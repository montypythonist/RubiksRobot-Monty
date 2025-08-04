import cv2
from numpy import float32
from json import load, dump
import kociemba
from collections import Counter
from pathlib import Path

# Base directory where the script is located
# TODO test directory fix on Pi's
BASE_DIR = Path(__file__).parent.resolve()
FACES_DIR = BASE_DIR / "faces"
JSON_PATH = BASE_DIR / "storing.json"

def crop(image_path):
    image_path = str(image_path)  # Ensure it's a string for OpenCV
    image = cv2.imread(image_path)

    if image is None:
        print(f"Failed to read image: {image_path}")
        return

    height, width, _ = image.shape
    square_size = min(width, height) // 5
    offset_x = (width - 3 * square_size) // 2
    offset_y = (height - 3 * square_size) // 2

    # Draw grid on the image
    for i in range(3):
        for j in range(3):
            x1, y1 = offset_x + j * square_size, offset_y + i * square_size
            x2, y2 = x1 + square_size, y1 + square_size
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Crop the image to include only the Rubik's Cube
    cropped_image = image[offset_y:offset_y + 3 * square_size, offset_x:offset_x + 3 * square_size]

    # Overwrite the original image file with the cropped version
    cv2.imwrite(image_path, cropped_image)


crop(FACES_DIR / "back.jpg")
crop(FACES_DIR / "down.jpg")
crop(FACES_DIR / "front.jpg")
crop(FACES_DIR / "left.jpg")
crop(FACES_DIR / "right.jpg")
crop(FACES_DIR / "up.jpg")

# BGR thresholds
# TODO fix incorrectly detected colors on Pi
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

def color(image_path, cube_side):
    image_path = str(image_path)
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image.")
        return

    h, w, _ = img.shape
    square_height = h // 3
    square_width = w // 3

    with open(JSON_PATH, 'r') as file:
        cube = load(file)

    for i in range(3):
        for j in range(3):
            y1 = i * square_height
            y2 = (i + 1) * square_height
            x1 = j * square_width
            x2 = (j + 1) * square_width
            square = img[y1:y2, x1:x2]
            color_val = get_dominant_color(square)
            color_name = color_checker(color_val)
            k = i * 3 + j
            cube[cube_side][k] = color_name

    with open(JSON_PATH, 'w') as file:
        dump(cube, file, indent=4)

color(FACES_DIR / "back.jpg", "back")
color(FACES_DIR / "down.jpg", "down")
color(FACES_DIR / "front.jpg", "front")
color(FACES_DIR / "left.jpg", "left")
color(FACES_DIR / "right.jpg", "right")
color(FACES_DIR / "up.jpg", "up")

def loading(filename):
    filename = str(filename)
    with open(filename, 'r') as file:
        return load(file)

def checkunknown(cube):
    for face, stickers in cube.items():
        for i, color in enumerate(stickers):
            if color == "unknown":
                return False
    return True

def facemapping(cube):
    color_to_face = {}
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

    for face in ['U', 'D', 'F', 'B', 'L', 'R']:
        if counts[face] != 9:
            print(f"Invalid count for face '{face}': {counts[face]}")
            return False

    return True

def solution(cube):
    if not checkunknown(cube):
        print("\n\n\nColors detected incorrectly!\n\n"
              f"Correct Detection: {checkunknown(cube)}\n"
              f"Validity: {validity(cube)}\n\n\n")
        return "Failed"

    color_to_face = facemapping(cube)
    cube_string = kociembastring(cube, color_to_face)

    if not validity(cube_string):
        print("\n\n\nColors detected incorrectly!\n\n"
              f"Correct Detection: {checkunknown(cube)}\n"
              f"Validity: {validity(cube_string)}\n\n\n")
        return "Failed"

    solution_str = kociemba.solve(cube_string)
    if not solution_str:
        return ""

    print("\n\n\n" + solution_str + "\n\n\n")
    return "Successful!"

cube_state = loading(JSON_PATH)
print(type(solution(cube_state)))
print(solution(cube_state))
cube = solution(cube_state)
moves = cube.split(" ") if isinstance(cube, str) else []

class clockwise:
    def F(): return
    def R(): return
    def U(): return
    def L(): return
    def B(): return
    def D(): return

class counterclockwise:
    def F(): return
    def R(): return
    def U(): return
    def L(): return
    def B(): return
    def D(): return

class doubleclockwise:
    def F(): return
    def R(): return
    def U(): return
    def L(): return
    def B(): return
    def D(): return

for move in moves:
    if move == "F": clockwise.F()
    elif move == "R": clockwise.R()
    elif move == "U": clockwise.U()
    elif move == "L": clockwise.L()
    elif move == "B": clockwise.B()
    elif move == "D": clockwise.D()
    elif move == "F'": counterclockwise.F()
    elif move == "R'": counterclockwise.R()
    elif move == "U'": counterclockwise.U()
    elif move == "L'": counterclockwise.L()
    elif move == "B'": counterclockwise.B()
    elif move == "D'": counterclockwise.D()
    elif move == "F2": doubleclockwise.F()
    elif move == "R2": doubleclockwise.R()
    elif move == "U2": doubleclockwise.U()
    elif move == "L2": doubleclockwise.L()
    elif move == "B2": doubleclockwise.B()
    elif move == "D2": doubleclockwise.D()
