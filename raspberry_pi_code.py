import cv2
import time
import requests
import serial
import RPi.GPIO as GPIO

BUZZER = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER, GPIO.OUT)

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def send_alert(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

face_cascade = cv2.CascadeClassifier(
    'haarcascade_frontalface_default.xml'
)

eye_cascade = cv2.CascadeClassifier(
    'haarcascade_eye.xml'
)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*'MJPG')
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

closed_frames = 0
drowsy_level = 0
yawn_counter = 0
frame_count = 0

telegram_sent = False

while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera not found")
        break

    frame_count += 1

    if frame_count % 3 != 0:
        continue

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )

    eyes_detected = 0

    for (x, y, w, h) in faces:

        roi_gray = gray[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.1,
            minNeighbors=3
        )

        eyes_detected = len(eyes)

        lower_face = roi_gray[h//2:h, :]

        mouth_darkness = lower_face.mean()

        if mouth_darkness < 50:

            yawn_counter += 1
            drowsy_level += 1

        else:

            yawn_counter = 0

        if yawn_counter > 6:

            cv2.putText(
                frame,
                "YAWNING!",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

            GPIO.output(BUZZER, GPIO.HIGH)
            time.sleep(0.15)
            GPIO.output(BUZZER, GPIO.LOW)

    if eyes_detected == 0:

        closed_frames += 1
        drowsy_level += 2

    else:

        closed_frames = 0

        if drowsy_level > 0:
            drowsy_level -= 1

    if drowsy_level > 50:

        cv2.putText(
            frame,
            "DROWSY ALERT",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        GPIO.output(BUZZER, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(BUZZER, GPIO.LOW)

        if not telegram_sent:

            send_alert(
                f"WARNING! Driver is highly drowsy. Level: {drowsy_level}"
            )

            telegram_sent = True

    else:
        telegram_sent = False

    if drowsy_level < 20:

        status = "LEVEL 1"
        arduino.write(b'1')

    elif drowsy_level < 40:

        status = "LEVEL 2"
        arduino.write(b'2')

    elif drowsy_level < 60:

        status = "LEVEL 3"
        arduino.write(b'3')

    else:

        status = "LEVEL 4"
        arduino.write(b'4')

    cv2.putText(
        frame,
        f"Drowsy Level: {drowsy_level}",
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        status,
        (10, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Press R to Reset",
        (10, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1
    )

    cv2.imshow(
        "Drowsiness Detection",
        frame
    )

    key = cv2.waitKey(1)

    if key == ord('q'):
        break

    if key == 27:
        break

    if key == ord('r'):

        drowsy_level = 0
        closed_frames = 0
        yawn_counter = 0
        telegram_sent = False

        arduino.write(b'0')

        print("System Reset")

cap.release()

cv2.destroyAllWindows()

GPIO.cleanup()
