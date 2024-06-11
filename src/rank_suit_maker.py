import cv2
import numpy as np
import requests
import os
from io import BytesIO
from PIL import Image

# ESP32-CAM URL
CAM_URL = "http://192.168.100.124/cam-hi.jpg"  # Change to your ESP32-CAM IP

# Function to capture image from ESP32-CAM
def capture_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img)
    return img

# Function to save the captured image with the specified rank and suit
def save_image(image, rank, suit, path):
    rank_path = os.path.join(path, rank + '.jpg')
    suit_path = os.path.join(path, suit + '.jpg')
    
    # Save rank and suit images
    cv2.imwrite(rank_path, image)
    cv2.imwrite(suit_path, image)
    print(f'Saved {rank_path} and {suit_path}')

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    imgs_path = os.path.join(path, "src", "maker")
    
    # Create the directory if it doesn't exist
    os.makedirs(imgs_path, exist_ok=True)

    while True:
        # Capture the image
        image = capture_image(CAM_URL)
        
        # Display the image
        cv2.imshow("Captured Image", image)
        
        # Get the rank and suit from the user
        rank = input("Enter the rank (e.g., Ace, Two, Three, etc.): ")
        suit = input("Enter the suit (e.g., Hearts, Diamonds, Clubs, Spades): ")
        
        # Save the image with the specified rank and suit
        save_image(image, rank, suit, imgs_path)
        
        # Display the saved images
        cv2.imshow("Rank Image", cv2.imread(os.path.join(imgs_path, rank + '.jpg')))
        cv2.imshow("Suit Image", cv2.imread(os.path.join(imgs_path, suit + '.jpg')))
        
        # Check if the user wants to capture another image
        cont = input("Do you want to capture another image? (y/n): ")
        if cont.lower() != 'y':
            break
    
    # Release the camera and close the windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
