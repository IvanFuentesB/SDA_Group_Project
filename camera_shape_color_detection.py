import cv2
import numpy as np

# ──────────────────────────────────────────────
# CAMERA SETUP
# ──────────────────────────────────────────────
DROIDCAM_INDEX = 1
print(f"🎥 Trying to open DroidCam on index {DROIDCAM_INDEX} ...")
cap = cv2.VideoCapture(DROIDCAM_INDEX)  # cap = camera capture object

if not cap.isOpened():
    print("❌ Could not open DroidCam on index 1. Trying all indexes...")
    found = False
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"✅ Found working camera at index {i}")
            DROIDCAM_INDEX = i
            found = True
            break
    if not found:
        print("❌ No working camera found.")
        exit()

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
cap.set(cv2.CAP_PROP_EXPOSURE, -1)

print(f"✅ Using camera index {DROIDCAM_INDEX}")
print("🎥 Starting detection... Press 'q' to quit.")

# ──────────────────────────────────────────────
# DETECTION CONSTANTS
# ──────────────────────────────────────────────
MIN_AREA = 1200  # Minimum contour area to consider something a shape
KERNEL = np.ones((5, 5), np.uint8)  # Used for morphological operations (cleaning masks)

# HSV color ranges (for color detection)
RED1 = (np.array([0, 120, 70]), np.array([10, 255, 255]))
RED2 = (np.array([170, 120, 70]), np.array([180, 255, 255]))
GREEN = (np.array([35, 80, 80]), np.array([85, 255, 255]))
BLUE = (np.array([90, 80, 80]), np.array([130, 255, 255]))
YELLOW = (np.array([20, 120, 120]), np.array([35, 255, 255]))

# ──────────────────────────────────────────────
# IMAGE ENHANCEMENT
# ──────────────────────────────────────────────
def enhance_frame(frame):
    # Convert to LAB color space — separates brightness (L) from color (A,B)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # CLAHE = Contrast Limited Adaptive Histogram Equalization
    # It improves contrast and visibility in different lighting
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge channels back and convert to BGR again
    frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # Add a bit of sharpening
    blur = cv2.GaussianBlur(frame, (0, 0), 1.5)
    return cv2.addWeighted(frame, 1.4, blur, -0.4, 0)

# ──────────────────────────────────────────────
# SHAPE & COLOR DETECTION
# ──────────────────────────────────────────────
def detect_shape(c):
    # Perimeter of contour
    peri = cv2.arcLength(c, True)

    # Approximate contour shape (reduces number of points)
    approx = cv2.approxPolyDP(c, 0.025 * peri, True)
    v = len(approx)  # number of vertices
    area = cv2.contourArea(c)
    if peri == 0:
        return "Unknown"

    # Circularity formula: (4π * area) / (perimeter²)
    circ = 4 * np.pi * area / (peri * peri)

    # Classify shapes based on vertices and circularity
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
    # Create mask for just this contour
    mask = np.zeros(hsv.shape[:2], np.uint8)
    cv2.drawContours(mask, [c], -1, 255, -1)

    # Helper to count pixels inside contour for each color range
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

# ──────────────────────────────────────────────
# FIND BLACK MAT
# ──────────────────────────────────────────────
def find_black_mat(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask_dark = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(mask_dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    if w * h < 10000:
        return None

    pad_x, pad_y = int(w * 0.1), int(h * 0.1)
    return (max(0, x - pad_x), max(0, y - pad_y), w + 2 * pad_x, h + 2 * pad_y)

def draw_label(img, text, pos, color=(255, 255, 255)):
    # Draw outlined label text for readability
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────
mat_bbox = None

while True:
    ok, frame = cap.read()
    if not ok:
        print("⚠️ Frame read error.")
        break

    frame = cv2.resize(frame, (960, 540))

    # Adjust exposure automatically if image is too dark
    if np.mean(frame) < 50:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
        cap.set(cv2.CAP_PROP_EXPOSURE, -1)

    # Detect black mat first
    if mat_bbox is None:
        bbox = find_black_mat(frame)
        if bbox:
            mat_bbox = bbox
            print(f"✅ Mat detected at {bbox}")
        else:
            draw_label(frame, "Detecting mat...", (50, 60))
            cv2.imshow("Block Detection", frame)
            if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
                break
            continue

    # Crop to detected mat
    x, y, w, h = mat_bbox
    crop = frame[y:y+h, x:x+w]
    enhanced = enhance_frame(crop)
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)

    # Create mask for all target colors
    mask_total = (
        cv2.inRange(hsv, *RED1) | cv2.inRange(hsv, *RED2) |
        cv2.inRange(hsv, *GREEN) | cv2.inRange(hsv, *BLUE) |
        cv2.inRange(hsv, *YELLOW)
    )
    # Clean the mask using morphology
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, KERNEL)
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, KERNEL)

    detection = enhanced.copy()
    contours, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:
            continue
        color = color_by_mask(hsv, c)
        shape = detect_shape(c)
        if color == "Unknown":
            continue
        x2, y2, w2, h2 = cv2.boundingRect(c)
        cv2.rectangle(detection, (x2, y2), (x2+w2, y2+h2), (0, 0, 0), 2)
        draw_label(detection, f"{color} {shape}", (x2, y2 - 10))

    # ──────────────────────────────────────────────
    # MAIN DISPLAY
    # ──────────────────────────────────────────────
    cv2.imshow("Block Detection", detection)

    # Uncomment below to debug:
    # cv2.imshow("Raw Frame", frame)
    # cv2.imshow("Enhanced", enhanced)
    # cv2.imshow("HSV", cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    # cv2.imshow("Color Mask", mask_total)

    # Quit key
    if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
print("🛑 Detection stopped.")
