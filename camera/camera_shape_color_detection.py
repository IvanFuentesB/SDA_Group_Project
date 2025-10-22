import cv2
import numpy as np
import time

# ──────────────────────────────────────────────
# SETTINGS (Mode selection)
# "steady" = shape must appear for a few seconds
# "limited" = only accepts one instance of each unique shape
# ──────────────────────────────────────────────
DETECTION_MODE = "steady"  # choose between "steady" or "limited"
CONFIRM_TIME = 2.0  # seconds a shape must persist to be accepted

# ──────────────────────────────────────────────
# CAMERA SETUP
# ──────────────────────────────────────────────
DROIDCAM_INDEX = 1
print(f"🎥 Trying to open DroidCam on index {DROIDCAM_INDEX} ...")
cap = cv2.VideoCapture(DROIDCAM_INDEX)

# Try all camera indexes if the first fails
if not cap.isOpened():
    print("❌ Could not open DroidCam on index 1. Trying all indexes...")
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"✅ Found working camera at index {i}")
            DROIDCAM_INDEX = i
            break
    else:
        print("❌ No working camera found.")
        exit()

# Configure camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # set format

print(f"✅ Using camera index {DROIDCAM_INDEX}")
print("🎥 Starting detection... Press 'q' to quit.")

# ──────────────────────────────────────────────
# DETECTION CONSTANTS
# ──────────────────────────────────────────────
MIN_AREA = 1200  # smallest contour area to consider a valid shape
KERNEL = np.ones((5, 5), np.uint8)  # used for cleaning up masks (morphological ops)

# Color ranges in HSV format
RED1 = (np.array([0, 120, 70]), np.array([10, 255, 255]))
RED2 = (np.array([170, 120, 70]), np.array([180, 255, 255]))
GREEN = (np.array([35, 80, 80]), np.array([85, 255, 255]))
BLUE = (np.array([90, 80, 80]), np.array([130, 255, 255]))
YELLOW = (np.array([20, 120, 120]), np.array([35, 255, 255]))


# ──────────────────────────────────────────────
# SHAPE CLASS
# ──────────────────────────────────────────────
class Shape:
    def __init__(self, color, shape_type, position):
        self.color = color
        self.shape_type = shape_type
        self.position = position  # (x, y)

    # __repr__ defines how it looks when printed
    def __repr__(self):
        return f"Shape(color='{self.color}', type='{self.shape_type}', pos={self.position})"


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def enhance_frame(frame):
    # LAB separates brightness from color → improves contrast
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # CLAHE improves local contrast (important for weak lighting)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge again and sharpen
    frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    blur = cv2.GaussianBlur(frame, (0, 0), 1.5)
    return cv2.addWeighted(frame, 1.4, blur, -0.4, 0)


def detect_shape(c):
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.025 * peri, True)
    v = len(approx)
    area = cv2.contourArea(c)
    if peri == 0:
        return "Unknown"

    # Circularity = 4πA/P² (close to 1 if perfect circle)
    circ = 4 * np.pi * area / (peri * peri)

    # Classification by vertex count + circularity
    if circ > 0.83:
        return "Circle"
    if v == 3:
        return "Triangle"
    if 4 <= v <= 6:
        return "Quadrilateral"
    if v > 6:
        return "Circle"
    return "Unknown"


def color_by_mask(hsv, c):
    mask = np.zeros(hsv.shape[:2], np.uint8)
    cv2.drawContours(mask, [c], -1, 255, -1)

    # helper function → coverage of a color range inside mask
    def cov(low, high):
        m = cv2.inRange(hsv, low, high)
        return cv2.countNonZero(cv2.bitwise_and(m, m, mask=mask))

    covs = {
        "Red": cov(*RED1) + cov(*RED2),
        "Green": cov(*GREEN),
        "Blue": cov(*BLUE),
        "Yellow": cov(*YELLOW)
    }

    color, best = max(covs.items(), key=lambda x: x[1])
    total = sum(covs.values())

    if total == 0 or best < 0.6 * total:
        return "Unknown"
    return color


def draw_label(img, text, pos, color=(255, 255, 255)):
    # draws text with outline (readable on all backgrounds)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)


# ──────────────────────────────────────────────
# DETECTION LOOP
# ──────────────────────────────────────────────
last_shape = None
detection_start_time = 0
confirmed_shapes = []  # all confirmed and ready to send to game

while True:
    ok, frame = cap.read()
    if not ok:
        print("⚠️ Frame read error.")
        break

    frame = cv2.resize(frame, (960, 540))
    enhanced = enhance_frame(frame)
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)

    # Combine masks for all colors
    mask_total = (
        cv2.inRange(hsv, *RED1) | cv2.inRange(hsv, *RED2) |
        cv2.inRange(hsv, *GREEN) | cv2.inRange(hsv, *BLUE) |
        cv2.inRange(hsv, *YELLOW)
    )

    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, KERNEL)
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, KERNEL)

    contours, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detection = enhanced.copy()

    detected_shapes = []
    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:
            continue
        color = color_by_mask(hsv, c)
        shape_type = detect_shape(c)
        if color == "Unknown":
            continue
        x, y, w, h = cv2.boundingRect(c)
        center = (int(x + w / 2), int(y + h / 2))
        draw_label(detection, f"{color} {shape_type}", (x, y - 10))
        detected_shapes.append(Shape(color, shape_type, center))

    # ──────────────────────────────────────────────
    # SHAPE VALIDATION LOGIC
    # ──────────────────────────────────────────────
    if detected_shapes:
        shape = detected_shapes[0]

        if DETECTION_MODE == "steady":
            # must remain same for CONFIRM_TIME seconds
            if last_shape and (shape.color, shape.shape_type) == (last_shape.color, last_shape.shape_type):
                if time.time() - detection_start_time >= CONFIRM_TIME:
                    confirmed_shapes.append(shape)
                    print(f"✅ Confirmed shape after {CONFIRM_TIME}s:", shape)
                    detection_start_time = time.time()
            else:
                last_shape = shape
                detection_start_time = time.time()

        elif DETECTION_MODE == "limited":
            # instantly accepts new unique combos
            if not last_shape or (shape.color, shape.shape_type) != (last_shape.color, last_shape.shape_type):
                confirmed_shapes.append(shape)
                print("✅ Accepted new unique shape:", shape)
                last_shape = shape

    cv2.imshow("Block Detection", detection)
    if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
print("🛑 Detection stopped.")

# ──────────────────────────────────────────────
# PART 2 — FUNCTION TO ACCESS DETECTED SHAPES
# ──────────────────────────────────────────────
# this allows the game to call get_detected_shapes()
# and fetch whatever the camera confirmed so far

def get_detected_shapes():
    """
    Returns a list of confirmed Shape objects
    for use in game.py. Each Shape includes:
    - shape.color        (str)
    - shape.shape_type   (str)
    - shape.position     (tuple of x, y)
    """
    return confirmed_shapes


#Smth for Razvan}
## At the top of game.py, just import:

# from camera_shape_color_detection import get_detected_shapes, Shape


##Then, inside your game loop:

# shapes_to_draw = get_detected_shapes()