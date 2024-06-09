import cv2
# import numpy as np

# URL of the video stream from ESP32-CAM
url = "http://192.168.100.124:81/stream"

# Open the video stream
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform edge detection
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours
    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # Adjust the contour area threshold as needed
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

    cv2.imshow('ESP32-CAM', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
