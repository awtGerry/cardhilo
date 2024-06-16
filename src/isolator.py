import cv2
import numpy as np
import requests
import time
import os

import cards

img_path = os.path.dirname(os.path.abspath(__file__)) + '/imgs/new/'

if not os.path.exists(img_path):
    os.makedirs(img_path)

IM_WIDTH = 800
IM_HEIGHT = 600

RANK_WIDTH = 70
RANK_HEIGHT = 125

SUIT_WIDTH = 70
SUIT_HEIGHT = 100

# URL for the ESP32-CAM image
esp32_cam_url = 'http://192.168.100.124/cam-hi.jpg'

# Function to fetch image from ESP32-CAM
def fetch_image(url):
    response = requests.get(url)
    img_arr = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    return img

# Use counter variable to switch from isolating Rank to isolating Suit
i = 1

for Name in ['Ace','Two','Three','Four','Five','Six','Seven','Eight',
             'Nine','Ten','Jack','Queen','King','Spades','Diamonds',
             'Clubs','Hearts']:

    filename = Name + '.jpg'
    print('Press "p" to take a picture of ' + filename)

    while True:
        image = fetch_image(esp32_cam_url)
        cv2.imshow("Card", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("p"):
            break

    # Pre-process image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    retval, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)

    # Find contours and sort them by size
    cnts, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    # Assume largest contour is the card. If there are no contours, print an error
    flag = 0
    image2 = image.copy()

    if len(cnts) == 0:
        print('No contours found!')
        continue

    card = cnts[0]

    # Approximate the corner points of the card
    peri = cv2.arcLength(card, True)
    approx = cv2.approxPolyDP(card, 0.01 * peri, True)
    pts = np.float32(approx)

    x, y, w, h = cv2.boundingRect(card)

    # Flatten the card and convert it to 200x300
    warp = cards.flattener(image, pts, w, h)

    # Grab corner of card image, zoom, and threshold
    corner = warp[0:160, 0:64]
    corner_zoom = cv2.resize(corner, (0, 0), fx=2.5, fy=2.5)
    corner_blur = cv2.GaussianBlur(corner_zoom, (5, 5), 0)
    retval, corner_thresh = cv2.threshold(corner_blur, 155, 255, cv2.THRESH_BINARY_INV)

    # Isolate suit or rank
    if i <= 13:  # Isolate rank
        rank = corner_thresh[20:285, 0:130]  # Grabs portion of image that shows rank
        rank = cv2.cvtColor(rank, cv2.COLOR_BGR2GRAY)
        rank_cnts, hier = cv2.findContours(rank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rank_cnts = sorted(rank_cnts, key=cv2.contourArea, reverse=True)
        x, y, w, h = cv2.boundingRect(rank_cnts[0])
        rank_roi = rank[y:y + h, x:x + w]
        rank_sized = cv2.resize(rank_roi, (RANK_WIDTH, RANK_HEIGHT), 0, 0)
        final_img = rank_sized

    # if i > 13:  # Isolate suit
    #     suit = corner_thresh[350:640, 0:280]  # Grabs portion of image that shows suit
    #     suit = cv2.cvtColor(suit, cv2.COLOR_BGR2GRAY)
    #     suit = cv2.cvtColor(suit, cv2.COLOR_BGR2GRAY)
    #     suit_cnts, hier = cv2.findContours(suit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     suit_cnts = sorted(suit_cnts, key=cv2.contourArea, reverse=True)
    #     x, y, w, h = cv2.boundingRect(suit_cnts[0])
    #     suit_roi = suit[y:y + h, x:x + w]
    #     suit_sized = cv2.resize(suit_roi, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)
    #     final_img = suit_sized

    cv2.imshow("Image", final_img)

    # Save image
    print('Press "c" to continue.')
    key = cv2.waitKey(0) & 0xFF
    if key == ord('c'):
        cv2.imwrite(img_path + filename, final_img)

    # Quit if the user presses 'q'
    if key == ord('q'):
        break

    i = i + 1

cv2.destroyAllWindows()
