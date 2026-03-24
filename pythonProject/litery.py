import cv2
import mediapipe as mp
import math
import numpy as np

# Inicjalizacja MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)


# Funkcja obliczająca kąt między trzema punktami (np. ramię-łokieć-nadgarstek)
def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])  # Punkt początkowy
    b = np.array([b.x, b.y])  # Środek (staw)
    c = np.array([c.x, c.y])  # Punkt końcowy

    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = math.degrees(radians)

    # Utrzymywanie kąta w zakresie [0, 180] dla prostoty
    angle = abs(angle)
    if angle > 180.0:
        angle = 360 - angle

    return angle


cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Nie można odebrać klatki z kamery.")
        break

    # Przetwarzanie obrazu
    image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    current_letter = "?"
    color = (0, 0, 255)  # Czerwony dla braku wykrycia

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 1. Pobranie kluczowych punktów
        try:
            # Ręce
            l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            l_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            r_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            # Nogi i biodra
            l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
            r_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
            l_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            r_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

            # 2. Obliczenie kluczowych kątów i odległości
            l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
            r_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)
            l_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)

            # 3. Logika rozpoznawania (heurystyka)

            # --- Litera I (Ciało pionowe, ręce blisko) ---
            if (l_arm_angle < 40 and r_arm_angle < 40 and  # Ręce zgięte przy ciele
                    l_wrist.y > l_hip.y and r_wrist.y > r_hip.y and  # Nadgarstki poniżej bioder
                    abs(l_ankle.x - r_ankle.x) < 0.1):  # Stopy razem
                current_letter = "I"
                color = (0, 255, 0)

            # --- Litera T (Ramiona poziomo, nogi złączone) ---
            elif (abs(l_wrist.y - l_shoulder.y) < 0.1 and abs(
                    r_wrist.y - r_shoulder.y) < 0.1 and  # Ręce na wysokości ramion
                  abs(l_ankle.x - r_ankle.x) < 0.15):  # Stopy razem
                current_letter = "T"
                color = (0, 255, 0)

            # --- Litera Y (Ramiona do góry V, nogi złączone) ---
            elif (l_wrist.y < l_shoulder.y and r_wrist.y < r_shoulder.y and  # Nadgarstki powyżej ramion
                  l_arm_angle > 150 and r_arm_angle > 150 and  # Ręce proste
                  l_wrist.x < l_shoulder.x and r_wrist.x > r_shoulder.x):  # Rozszerzone V
                current_letter = "Y"
                color = (0, 255, 0)

            # --- Litera L (Lewa noga vertical, prawa horiz, obie proste) ---
            elif (abs(r_hip_angle - 90) < 30 and  # Prawe biodro zgięte ~90 stopni (noga do przodu/boku)
                  calculate_angle(r_hip, r_knee, r_ankle) > 150 and  # Prawa noga prosta w kolanie
                  abs(l_shoulder.x - l_ankle.x) < 0.15):  # Lewa strona ciała w pionie
                current_letter = "L"
                color = (0, 255, 0)

        except Exception as e:
            pass  # Pomiń klatkę, jeśli nie wszystkie punkty są widoczne

    # Wyświetlanie wyniku
    cv2.rectangle(image, (0, 0), (250, 70), (0, 0, 0), -1)
    cv2.putText(image, f"Litera: {current_letter}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3, cv2.LINE_AA)

    cv2.imshow('TYLI Recognition (Full Body)', image)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()