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
    image = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

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

            # Dodatkowe punkty do walidacji pionu
            l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            # 2. Obliczenie kluczowych kątów i odległości
            l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # --- STAŁE PARAMETRY TOLERANCJI ---
            eps = 0.15  # Standardowy margines (np. dla wysokości rąk w T i L)
            eps_narrow = 0.12  # Wąski margines dla litery I (ręce blisko bioder)
            straight = 145  # Próg kąta (im mniejszy, tym łatwiej o detekcję przy zgiętych łokciach)

            # --- LOGIKA ROZPOZNAWANIA LITER ---

            # 1. Litera Y: Obie ręce wyprostowane i uniesione W GÓRĘ
            # Jeśli nadgarstki są powyżej barków (y_wrist < y_shoulder), to uznajemy to za Y
            if (l_arm_angle > straight + 5 and r_arm_angle > straight + 5 and
                    l_wrist.y < l_shoulder.y and r_wrist.y < r_shoulder.y):
                current_letter = "Y"
                color = (0, 255, 0)

            # 2. Litera I: Obie ręce wyprostowane W DÓŁ (wzdłuż tułowia)
            # Nadgarstki muszą być poniżej barków i blisko osi ciała (mały eps_narrow)
            elif (l_arm_angle > straight and r_arm_angle > straight and
                  l_wrist.y > l_shoulder.y and r_wrist.y > r_shoulder.y and
                  abs(l_wrist.x - l_shoulder.x) < eps_narrow and
                  abs(r_wrist.x - r_shoulder.x) < eps_narrow):
                current_letter = "I"
                color = (0, 255, 0)

            # 3. Litera T: Obie ręce wyprostowane POZIOMO
            # Nadgarstki na wysokości barków (różnica y mniejsza niż eps)
            elif (l_arm_angle > straight and r_arm_angle > straight and
                  abs(l_wrist.y - l_shoulder.y) < eps and
                  abs(r_wrist.y - r_shoulder.y) < eps):
                current_letter = "T"
                color = (0, 255, 0)

            # 4. Litera L: Prawa ręka w górę (na ekranie lewo), lewa ręka poziomo (na ekranie prawo)
            # Uwaga: sprawdzamy czy r_wrist jest nad barkiem, a l_wrist na wysokości barku
            elif (r_arm_angle > straight and l_arm_angle > straight and
                  r_wrist.y < r_shoulder.y and abs(r_wrist.x - r_shoulder.x) < eps and
                  abs(l_wrist.y - l_shoulder.y) < eps and l_wrist.x < l_shoulder.x):
                current_letter = "L"
                color = (0, 255, 0)

        except Exception as e:
            pass  # Pomiń klatkę, jeśli nie wszystkie punkty są widoczne

    # Wyświetlanie wyniku
    cv2.rectangle(image, (0, 0), (270, 70), (0, 0, 0), -1)
    cv2.putText(image, f"Litera: {current_letter}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3, cv2.LINE_AA)

    cv2.imshow('TYLI Recognition (Full Body)', image)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()