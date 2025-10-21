import cv2
import numpy as np

# ──────────────────────────────────────────────
# CAMERA SETUP
# ──────────────────────────────────────────────
cap = cv2.VideoCapture(1)  # Change to 0 if you use built-in camera

if not cap.isOpened():
    print("❌ Error: Could not open camera.")
    exit()

# ──────────────────────────────────────────────
# COLOR RANGES (HSV)
# ──────────────────────────────────────────────
color_ranges = {
    "Red": ([0, 120, 70], [10, 255, 255]),
    "Red2": ([170, 120, 70], [180, 255, 255]),  # wrap-around red
    "Blue": ([90, 100, 50], [130, 255, 255]),
    "Green": ([35, 50, 50], [85, 255, 255]),
    "Yellow": ([20, 100, 100], [35, 255, 255])
}

# ──────────────────────────────────────────────
# FUNCTION: Detect shapes
# ──────────────────────────────────────────────
def detect_shape(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    vertices = len(approx)

    if vertices == 3:
        return "Triangle"
    elif vertices == 4:
        return "Quadrilateral"
    elif vertices > 8:
        return "Circle"
    return "Unknown"

# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame.")
        break

    # Resize for stability and optional crop
    frame = cv2.resize(frame, (1280, 800))
    frame = frame[100:620, 300:1080]  # Crop region of interest (adjust to your setup)

    # Slightly sharpen image
    kernel_sharp = np.array([[0, -1, 0],
                             [-1, 5, -1],
                             [0, -1, 0]])
    frame = cv2.filter2D(frame, -1, kernel_sharp)

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Build a combined mask for all colors
    mask_total = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for name, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        mask_total = cv2.bitwise_or(mask_total, mask)

    # Clean the mask (reduce noise)
    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 1000:
            continue  # Skip small objects

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)

        # Keep only roughly rectangular/square shapes
        if 0.5 < aspect_ratio < 2.0:
            shape = detect_shape(contour)

            # Average color in ROI
            roi = frame[y:y + h, x:x + w]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            avg_color = np.mean(hsv_roi.reshape(-1, 3), axis=0)
            h_val = avg_color[0]

            # Determine color by hue
            if h_val < 10 or h_val > 160:
                color_name = "Red"
            elif 20 < h_val < 35:
                color_name = "Yellow"
            elif 35 <= h_val < 85:
                color_name = "Green"
            elif 90 < h_val < 130:
                color_name = "Blue"
            else:
                color_name = "Unknown"

            # Draw box + label
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
            label = f"{color_name} {shape}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Show output
    cv2.imshow("Block Detection", frame)

    # Quit with 'q' or ESC
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
