import cv2
import mediapipe as mp
import numpy as np
import os

# ---------------- SETTINGS ----------------
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
PALETTE_HEIGHT = 100
DRAW_THICKNESS = 5
ERASER_THICKNESS = 50
SMOOTHING = 5
# ------------------------------------------

# MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# -------- LOAD PALETTE --------
palette_folder = "colors"
palette_images = []
palette_colors = []

if os.path.exists(palette_folder):
    files = sorted(os.listdir(palette_folder))
    for f in files:
        img = cv2.imread(os.path.join(palette_folder, f))
        if img is None:
            continue
        palette_images.append(img)

        name = f.lower()
        if "red" in name:
            palette_colors.append((0, 0, 255))
        elif "green" in name:
            palette_colors.append((0, 255, 0))
        elif "blue" in name:
            palette_colors.append((255, 0, 0))
        elif "eraser" in name:
            palette_colors.append((0, 0, 0))  # ERASER
        else:
            palette_colors.append((0, 0, 0))

if len(palette_images) == 0:
    print("❌ No palette images found!")
    exit()

draw_color = (0, 0, 255)

# -------- FINGER DETECTION --------
def fingers_up(hand):
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    lm = hand.landmark

    fingers = []
    fingers.append(lm[tips[0]].x < lm[pips[0]].x)  # Thumb

    for i in range(1, 5):
        fingers.append(lm[tips[i]].y < lm[pips[i]].y)

    return fingers

# --------------- MAIN ---------------
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    canvas = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    prev_x, prev_y = 0, 0
    points = []

    with mp_hands.Hands(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            # -------- PALETTE BAR --------
            section_width = FRAME_WIDTH // len(palette_images)
            palette_bar = np.zeros((PALETTE_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)

            for i, img in enumerate(palette_images):
                img = cv2.resize(img, (section_width, PALETTE_HEIGHT))
                palette_bar[:, i * section_width:(i + 1) * section_width] = img

            frame[0:PALETTE_HEIGHT, :] = palette_bar

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                fingers = fingers_up(hand)
                h, w, _ = frame.shape
                x = int(hand.landmark[8].x * w)
                y = int(hand.landmark[8].y * h)

                # -------- PALETTE SELECTION --------
                if y < PALETTE_HEIGHT:
                    index = x // section_width
                    if index < len(palette_colors):
                        draw_color = palette_colors[index]
                        cv2.rectangle(
                            frame,
                            (index * section_width, 0),
                            ((index + 1) * section_width, PALETTE_HEIGHT),
                            (0, 255, 255),
                            3
                        )
                    prev_x, prev_y = 0, 0
                    points.clear()

                # -------- DRAW / ERASE --------
                elif fingers[1] and not any(fingers[2:]):
                    points.append((x, y))
                    if len(points) > SMOOTHING:
                        points.pop(0)

                    avg_x = int(sum(p[0] for p in points) / len(points))
                    avg_y = int(sum(p[1] for p in points) / len(points))

                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = avg_x, avg_y

                    thickness = ERASER_THICKNESS if draw_color == (0, 0, 0) else DRAW_THICKNESS
                    cv2.line(canvas, (prev_x, prev_y), (avg_x, avg_y), draw_color, thickness)

                    prev_x, prev_y = avg_x, avg_y

                else:
                    prev_x, prev_y = 0, 0
                    points.clear()

            # -------- MERGE CANVAS --------
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, inv = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
            frame = cv2.bitwise_and(frame, inv)
            frame = cv2.bitwise_or(frame, canvas)

            cv2.imshow("✋ Hand Gesture Doodle", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# -------- RUN --------
if __name__ == "__main__":
    main()

