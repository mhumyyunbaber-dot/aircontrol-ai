import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import math
import os
from collections import deque


# ================== CONFIG ==================

SCREEN_W, SCREEN_H = pyautogui.size()

SMOOTHING = 0.85
CLICK_COOLDOWN = 0.5

# Scroll sensitivity
SCROLL_DIVISOR = 2

# Gesture stabilization
STABLE_FRAMES = 5


# ================== MEDIAPIPE ==================

BaseOptions = mp.tasks.BaseOptions
RunningMode = mp.tasks.vision.RunningMode
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "hand_landmarker.task"
)

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

hands = HandLandmarker.create_from_options(options)


# ================== CAMERA ==================

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# ================== WINDOW ==================

WINDOW_NAME = "AirControl AI"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ================== STATE ==================

prev_x = SCREEN_W / 2
prev_y = SCREEN_H / 2

scroll_prev_y = None
scroll_accumulator = 0.0

gesture_history = deque(
    maxlen=STABLE_FRAMES
)

current_gesture = "NONE"
previous_gesture = "NONE"

pinch_active = False

control_active = False

task_view_open = False
task_view_start_x = None


# ================== HELPERS ==================

def distance(p1, p2):

    return math.hypot(
        p1[0] - p2[0],
        p1[1] - p2[1]
    )


def angle(a, b, c):
    """
    Angle ABC in degrees.
    """

    ba = np.array([
        a.x - b.x,
        a.y - b.y
    ])

    bc = np.array([
        c.x - b.x,
        c.y - b.y
    ])

    denominator = (
        np.linalg.norm(ba)
        * np.linalg.norm(bc)
    )

    if denominator == 0:
        return 0

    cosine = np.dot(
        ba,
        bc
    ) / denominator

    cosine = np.clip(
        cosine,
        -1.0,
        1.0
    )

    return math.degrees(
        math.acos(cosine)
    )


def finger_extended(
    lm,
    mcp,
    pip,
    tip
):

    finger_angle = angle(
        lm[mcp],
        lm[pip],
        lm[tip]
    )

    return finger_angle > 155


def thumb_extended(lm):

    thumb_angle = angle(
        lm[2],
        lm[3],
        lm[4]
    )

    return thumb_angle > 150


def classify_gesture(lm, w, h):

    # -----------------------------------------
    # Finger states
    # -----------------------------------------

    index = finger_extended(
        lm, 5, 6, 8
    )

    middle = finger_extended(
        lm, 9, 10, 12
    )

    ring = finger_extended(
        lm, 13, 14, 16
    )

    pinky = finger_extended(
        lm, 17, 18, 20
    )

    thumb = thumb_extended(lm)


    # -----------------------------------------
    # Basic distances
    # -----------------------------------------

    thumb_tip = (
        lm[4].x * w,
        lm[4].y * h
    )

    index_tip = (
        lm[8].x * w,
        lm[8].y * h
    )

    index_mcp = (
        lm[5].x * w,
        lm[5].y * h
    )

    wrist = (
        lm[0].x * w,
        lm[0].y * h
    )

    pinch_distance = distance(
        thumb_tip,
        index_tip
    )

    palm_size = distance(
        wrist,
        (
            lm[9].x * w,
            lm[9].y * h
        )
    )


    # -----------------------------------------
    # Activation / Pause
    # Thumb + Index + Pinky
    # -----------------------------------------

    if (
        thumb
        and index
        and pinky
        and not middle
        and not ring
    ):
        return "TOGGLE"


    # -----------------------------------------
    # Pinch / Click
    # -----------------------------------------
    #
    # Important:
    # Pinch is detected from thumb/index
    # proximity AND the middle/ring/pinky
    # being folded.
    #
    # We DON'T require index to be extended.
    #

    if palm_size > 0:

        pinch_ratio = (
            pinch_distance / palm_size
        )

        if (
            pinch_ratio < 0.38
            and not middle
            and not ring
            and not pinky
        ):
            return "CLICK"


    # -----------------------------------------
    # Move
    # -----------------------------------------

    if (
        index
        and not middle
        and not ring
        and not pinky
    ):
        return "MOVE"


    # -----------------------------------------
    # Scroll
    # Index + Middle
    # -----------------------------------------

    if (
        index
        and middle
        and not ring
        and not pinky
    ):
        return "SCROLL"


    # -----------------------------------------
    # Task View
    # Three fingers
    # -----------------------------------------

    if (
        index
        and middle
        and ring
        and not pinky
    ):
        return "TASK VIEW"


    # -----------------------------------------
    # Palm / Show Desktop
    # -----------------------------------------

    if (
        thumb
        and index
        and middle
        and ring
        and pinky
    ):
        return "DESKTOP"


    # -----------------------------------------
    # Fist / Alt Tab
    # -----------------------------------------
    #
    # All four fingers folded AND thumb
    # is not extended.
    #
    # This keeps fist separate from pinch.
    #

    if (
        not index
        and not middle
        and not ring
        and not pinky
        and not thumb
    ):
        return "BACK"


    return "NONE"

def stabilize_gesture(gesture):

    gesture_history.append(
        gesture
    )

    if len(gesture_history) < STABLE_FRAMES:
        return "NONE"

    counts = {}

    for item in gesture_history:

        counts[item] = (
            counts.get(item, 0)
            + 1
        )

    best_gesture = max(
        counts,
        key=counts.get
    )

    if counts[best_gesture] >= 4:
        return best_gesture

    return "NONE"


# ================== MAIN LOOP ==================

try:

    while True:

        ok, frame = cap.read()

        if not ok:
            break


        # -------------------------------------
        # Mirror webcam
        # -------------------------------------

        frame = cv2.flip(
            frame,
            1
        )

        h, w, _ = frame.shape


        # -------------------------------------
        # MediaPipe
        # -------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = hands.detect(
            mp_image
        )


        raw_gesture = "NONE"


        if result.hand_landmarks:

            lm = result.hand_landmarks[0]

            raw_gesture = classify_gesture(
                lm,
                w,
                h
            )


        current_gesture = (
            stabilize_gesture(
                raw_gesture
            )
        )


        # -------------------------------------
        # Activation / Pause
        # -------------------------------------

        if (
            current_gesture == "TOGGLE"
            and previous_gesture != "TOGGLE"
        ):

            control_active = not control_active

            # Reset movement states
            scroll_prev_y = None
            scroll_accumulator = 0.0
            pinch_active = False


        # -------------------------------------
        # Cursor Movement
        # -------------------------------------

        if (
            control_active
            and current_gesture == "MOVE"
            and result.hand_landmarks
        ):

            lm = result.hand_landmarks[0]

            ix = lm[8].x * w
            iy = lm[8].y * h


            screen_x = np.interp(
                ix,
                [0, w],
                [0, SCREEN_W]
            )

            screen_y = np.interp(
                iy,
                [0, h],
                [0, SCREEN_H]
            )


            smooth_x = (
                prev_x
                + (
                    screen_x
                    - prev_x
                )
                * SMOOTHING
            )

            smooth_y = (
                prev_y
                + (
                    screen_y
                    - prev_y
                )
                * SMOOTHING
            )


            prev_x = smooth_x
            prev_y = smooth_y


            pyautogui.moveTo(
                int(smooth_x),
                int(smooth_y)
            )


        # -------------------------------------
        # Click
        # -------------------------------------

        if (
            control_active
            and current_gesture == "CLICK"
        ):

            if not pinch_active:

                pyautogui.click()

                pinch_active = True

        else:

            pinch_active = False


        # -------------------------------------
        # Scroll
        # -------------------------------------

        if (
            control_active
            and current_gesture == "SCROLL"
            and result.hand_landmarks
        ):

            lm = result.hand_landmarks[0]

            current_y = (
                lm[9].y * h
            )


            if scroll_prev_y is not None:

                delta = (
                    scroll_prev_y
                    - current_y
                )


                # Accumulate small movements
                scroll_accumulator += delta


                # Scroll once enough movement
                # has been accumulated
                if abs(
                    scroll_accumulator
                ) >= 2:

                    scroll_amount = int(
                        scroll_accumulator
                        / SCROLL_DIVISOR
                    )


                    if scroll_amount != 0:

                        pyautogui.scroll(
                            scroll_amount
                        )

                        scroll_accumulator = 0.0


            scroll_prev_y = current_y


        else:

            scroll_prev_y = None
            scroll_accumulator = 0.0


        # -------------------------------------
        # Palm → Show Desktop
        # -------------------------------------

        if (
            control_active
            and current_gesture == "DESKTOP"
            and previous_gesture != "DESKTOP"
        ):

            pyautogui.hotkey(
                "win",
                "d"
            )


        # -------------------------------------
        # Fist → Alt Tab
        # -------------------------------------

        if (
            control_active
            and current_gesture == "BACK"
            and previous_gesture != "BACK"
        ):

            pyautogui.hotkey(
                "alt",
                "tab"
            )


        # -------------------------------------
        # Task View
        # -------------------------------------

        if (
            control_active
            and current_gesture == "TASK VIEW"
        ):

            cx = int(
                result.hand_landmarks[0][9].x * w
            ) if result.hand_landmarks else None


            # Open Task View once
            if (
                previous_gesture
                != "TASK VIEW"
            ):

                pyautogui.hotkey(
                    "win",
                    "tab"
                )

                task_view_open = True
                task_view_start_x = cx


            # Swipe between apps
            elif (
                task_view_open
                and task_view_start_x is not None
                and cx is not None
            ):

                dx = (
                    cx
                    - task_view_start_x
                )


                if dx > 70:

                    pyautogui.press(
                        "right"
                    )

                    task_view_start_x = cx


                elif dx < -70:

                    pyautogui.press(
                        "left"
                    )

                    task_view_start_x = cx


        else:

            task_view_open = False
            task_view_start_x = None


        # -------------------------------------
        # UI
        # -------------------------------------

        cv2.putText(
            frame,
            "AIRCONTROL AI",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 255),
            3
        )


        status = (
            "ACTIVE"
            if control_active
            else "PAUSED"
        )


        cv2.putText(
            frame,
            f"Control: {status}",
            (40, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0)
            if control_active
            else (0, 0, 255),
            3
        )


        cv2.putText(
            frame,
            f"Mode: {current_gesture}",
            (40, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3
        )


        cv2.putText(
            frame,
            f"Raw: {raw_gesture}",
            (40, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )


        cv2.putText(
            frame,
            "Move | Pinch=Click | 2 Fingers=Scroll | Palm=Desktop | Fist=Back | 3 Fingers=Task View",
            (40, h - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.imshow(
            WINDOW_NAME,
            frame
        )


        # -------------------------------------
        # Quit
        # -------------------------------------

        if (
            cv2.waitKey(1)
            & 0xFF
            == ord("q")
        ):
            break


        previous_gesture = (
            current_gesture
        )


finally:

    cap.release()

    cv2.destroyAllWindows()

    hands.close()