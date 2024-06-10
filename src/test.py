import cv2
import os

file_path = './src/imgs/Ace.jpg'

# Check if the file exists
if not os.path.isfile(file_path):
    print(f"File {file_path} does not exist.")
else:
    img = cv2.imread(file_path, cv2.IMREAD_COLOR)
    if img is None:
        print(f"Failed to load image file: {file_path}")
    else:
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

