import cv2
import mediapipe as mp
import time
from boltiot import Bolt
api_key = "f9a2549d-8635-4e40-8f12-c9e1fc389731"
device_id  = "BOLT3848117"
mybolt = Bolt(api_key, device_id)
buzz = 0
# mybolt.analogWrite('3', '255')

def main():
    eye_blink_count = 0
    isClose = 0
    blink_flag = False
    cap = cv2.VideoCapture(0)  # You can change 0 to the camera index if you have multiple cameras
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignoring empty camera frame.")
                continue

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    left_eye_top = face_landmarks.landmark[159].y * frame.shape[0]  # Top eyelid of left eye
                    left_eye_bottom = face_landmarks.landmark[145].y * frame.shape[0]  # Bottom eyelid of left eye
                    right_eye_top = face_landmarks.landmark[386].y * frame.shape[0]  # Top eyelid of right eye
                    right_eye_bottom = face_landmarks.landmark[374].y * frame.shape[0]  # Bottom eyelid of right eyes field of view

                    # Calculate the vertical distance between the top and bottom eyelid landmarks
                    left_eye_height = left_eye_bottom - left_eye_top
                    right_eye_height = right_eye_bottom - right_eye_top
                    # Threshold value to determine if eyes are open or closed
                    eye_closed_threshold = 6  # Adjust this value according to your needs

                    # Draw rectangles around the eyes and label them as open or closed
                    if left_eye_height < eye_closed_threshold and right_eye_height < eye_closed_threshold:
                        isClose += 1
                        if blink_flag == False :
                            eye_blink_count += 1
                            blink_flag = True
                        # time.sleep(0)
                        cv2.rectangle(frame, (0, 0), (100, 50), (0, 0, 255), -1)
                        cv2.putText(frame, 'closed', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    else:
                        isClose = 0
                        blink_flag = False
                        cv2.rectangle(frame, (0, 0), (100, 50), (0, 255, 0), -1)
                        cv2.putText(frame, 'open', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.rectangle(frame, (0,51), (700, 150), (4, 55, 35), -1)
            cv2.putText(frame,"Blinked : " + str(eye_blink_count), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 225, 135), 4)

            if(isClose > 3) :
                buzz = 1
                cv2.rectangle(frame, (0, 252), (700, 150), (4, 55, 35), -1)
                cv2.putText(frame, "Drive Alert!! : Eyes are Closed for long time" , (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,(25, 225, 135), 4)
            else :
                buzz = 0

            if buzz == 1 :
                mybolt.digitalWrite('0', 'HIGH')
            else :
                mybolt.digitalWrite('0', 'LOW')
            cv2.imshow('Eyes Detection', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
