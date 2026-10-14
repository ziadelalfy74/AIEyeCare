import cv2
import numpy as np
import time
import os
import sys
import screen_brightness_control as sbc
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from win10toast import ToastNotifier

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class EyeCareEngine:
    def __init__(self, model_path):
        self.model_path = model_path
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            num_faces=1
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.BLINK_THRESHOLD = 0.22

        self.blink_count = 0
        self.consecutive_frames = 0
        self.start_time = time.time()
        self.last_blink_time = time.time()  
        self.last_notification_time = 0
        self.toaster = ToastNotifier()
        
        self.smoothed_brightness = 100
        self.current_set_brightness = 80
        self.last_brightness_change_time = time.time()
        self.BRIGHTNESS_DELAY = 2.0

    def calculate_ear(self, eye_indices, landmarks, w, h):
        try:
            p2 = np.array([landmarks[eye_indices[1]].x * w, landmarks[eye_indices[1]].y * h])
            p6 = np.array([landmarks[eye_indices[5]].x * w, landmarks[eye_indices[5]].y * h])
            p3 = np.array([landmarks[eye_indices[2]].x * w, landmarks[eye_indices[2]].y * h])
            p5 = np.array([landmarks[eye_indices[4]].x * w, landmarks[eye_indices[4]].y * h])
            p1 = np.array([landmarks[eye_indices[0]].x * w, landmarks[eye_indices[0]].y * h])
            p4 = np.array([landmarks[eye_indices[3]].x * w, landmarks[eye_indices[3]].y * h])
            
            p2_p6 = np.linalg.norm(p2 - p6)
            p3_p5 = np.linalg.norm(p3 - p5)
            p1_p4 = np.linalg.norm(p1 - p4)
            
            return (p2_p6 + p3_p5) / (2.0 * p1_p4)
        except:
            return 0.3

    def process_frame(self, frame):
        h, w, c = frame.shape
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detection_result = self.detector.detect(mp_image)

        current_time = time.time()
        elapsed_total_time = current_time - self.start_time

        raw_ambient = int(np.mean(gray_frame))
        self.smoothed_brightness = int(0.95 * self.smoothed_brightness + 0.05 * raw_ambient)

        face_detected = False
        is_room_too_dark = self.smoothed_brightness < 40

        if not is_room_too_dark and detection_result.face_landmarks:
            face_detected = True
            for face_landmarks in detection_result.face_landmarks:
                left_ear = self.calculate_ear(self.LEFT_EYE_INDICES, face_landmarks, w, h)
                right_ear = self.calculate_ear(self.RIGHT_EYE_INDICES, face_landmarks, w, h)
                avg_ear = (left_ear + right_ear) / 2.0

                if avg_ear > 0:
                    if avg_ear < self.BLINK_THRESHOLD:
                        self.consecutive_frames += 1
                    else:
                        if self.consecutive_frames >= 2:
                            self.blink_count += 1
                            self.last_blink_time = time.time()  
                        self.consecutive_frames = 0
        else:
            self.last_blink_time = current_time

        minutes = max(elapsed_total_time / 60, 0.01)
        blink_rate_per_min = int(self.blink_count / minutes) if face_detected else 0

        target_brightness = self.current_set_brightness
        if self.smoothed_brightness < 40:
            target_brightness = 30
        elif 40 <= self.smoothed_brightness <= 79:
            target_brightness = 60
        elif 80 <= self.smoothed_brightness <= 90:
            target_brightness = 80
        else:
            target_brightness = 100

        if target_brightness != self.current_set_brightness:
            if current_time - self.last_brightness_change_time > self.BRIGHTNESS_DELAY:
                self.current_set_brightness = target_brightness
                try:
                    sbc.set_brightness(self.current_set_brightness)
                except:
                    pass
        else:
            self.last_brightness_change_time = current_time

        eye_strain_warning = False
        if face_detected and elapsed_total_time > 30:
            if blink_rate_per_min < 7 or (current_time - self.last_blink_time > 12):
                eye_strain_warning = True

        if eye_strain_warning and (current_time - self.last_notification_time > 30):
            try:
                self.toaster.show_toast(
                    title="AI Eye Care Alert",
                    msg="Low blink rate detected! Take a moment to blink and rest your eyes.",
                    icon_path=resource_path("icon.ico"),
                    duration=5,
                    threaded=True
                )
                self.last_notification_time = current_time
            except:
                pass

        return frame, self.blink_count, blink_rate_per_min, self.smoothed_brightness