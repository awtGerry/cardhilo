import cv2

# URL of the video stream from ESP32-CAM
url = "http://192.168.100.124:81/stream"

# Open the video stream
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow('ESP32-CAM', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
