import cv2
import numpy as np

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ Camera not found.")
    exit()

# Optional: try disabling auto-exposure
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
cap.set(cv2.CAP_PROP_EXPOSURE, -5)

RESIZE_W, RESIZE_H = 1280, 800
MIN_AREA = 1200
KERNEL = np.ones((5, 5), np.uint8)

RED1 = (np.array([0, 120, 70]), np.array([10, 255, 255]))
RED2 = (np.array([170, 120, 70]), np.array([180, 255, 255]))
GREEN = (np.array([35, 80, 80]), np.array([85, 255, 255]))
BLUE = (np.array([90, 80, 80]), np.array([130, 255, 255]))
YELLOW = (np.array([20, 120, 120]), np.array([35, 255, 255]))

# ──────────────────────────────────────────────
def enhance_frame(frame):
    """Mild sharpening + contrast."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # Gentle unsharp mask
    blur = cv2.GaussianBlur(frame, (0, 0), 1.5)
    return cv2.addWeighted(frame, 1.4, blur, -0.4, 0)

# ──────────────────────────────────────────────
def detect_shape(c):
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.025 * peri, True)
    v = len(approx)
    area = cv2.contourArea(c)
    if peri == 0:
        return "Unknown"
    circ = 4 * np.pi * area / (peri * peri)
    if circ > 0.83:
        return "Circle"
    if v == 3:
        return "Triangle"
    if 4 <= v <= 6:
        return "Quadrilateral"
    if v > 6:
        return "Circle"
    return "Unknown"

# ──────────────────────────────────────────────
def color_by_mask(hsv, c):
    mask = np.zeros(hsv.shape[:2], np.uint8)
    cv2.drawContours(mask, [c], -1, 255, -1)
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
    # Expand crop box by 10 %
    pad_x, pad_y = int(w * 0.1), int(h * 0.1)
    x, y = max(0, x - pad_x), max(0, y - pad_y)
    return (x, y, w + 2 * pad_x, h + 2 * pad_y)

# ──────────────────────────────────────────────
def draw_label(img, text, pos):
    """Readable text with black outline"""
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2, cv2.LINE_AA)

# ──────────────────────────────────────────────
mat_bbox = None

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.resize(frame, (RESIZE_W, RESIZE_H))

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

    x, y, w, h = mat_bbox
    crop = frame[y:y+h, x:x+w]
    crop = enhance_frame(crop)

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask_total = (
        cv2.inRange(hsv, *RED1) | cv2.inRange(hsv, *RED2) |
        cv2.inRange(hsv, *GREEN) | cv2.inRange(hsv, *BLUE) |
        cv2.inRange(hsv, *YELLOW)
    )
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, KERNEL)
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, KERNEL)

    contours, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:
            continue
        color = color_by_mask(hsv, c)
        shape = detect_shape(c)
        if color == "Unknown":
            continue
        x2, y2, w2, h2 = cv2.boundingRect(c)
        cv2.rectangle(crop, (x2, y2), (x2+w2, y2+h2), (0, 0, 0), 2)
        draw_label(crop, f"{color} {shape}", (x2, y2 - 10))

    cv2.imshow("Block Detection", crop)
    if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
