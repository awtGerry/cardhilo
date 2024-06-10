import cv2
import numpy as np
import requests
import os
from io import BytesIO
from PIL import Image

import cards

# ESP32-CAM URL
CAM_URL = "http://192.168.100.124/cam-hi.jpg"  # Change to your ESP32-CAM IP

# Function to capture image from ESP32-CAM
def capture_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img)
    return img

# Load the ranks and suits
path = os.path.dirname(os.path.abspath(__file__))
train_ranks = cards.load_ranks("src/imgs/")
train_suits = cards.load_suits("src/imgs/")

freq = cv2.getTickFrequency()

# Main loop
while True:
    # Load the image from the ESP32-CAM
    image = capture_image(CAM_URL)

    # timer to calculate framerate
    t1 = cv2.getTickCount()

    # Preprocess the image
    pre_proc = cards.preprocess_image(image)

    # Find and sort the contours of the cards
    cnts_sort, cnt_is_card = cards.find_cards(pre_proc)

    # If there are contours
    if len(cnts_sort) != 0:
        # Initialize the list of cards
        cards_list = []
        k = 0

        # for each contour detected
        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):
                # preprocess card
                cards_list.append(cards.preprocess_card(cnts_sort[i], image))

                # find best rank and suit matches
                cards_list[k].best_rank_match, cards_list[k].best_suit_match, cards_list[k].rank_diff, cards_list[k].suit_diff = cards.match_card(cards_list[k], train_ranks, train_suits)

                # draw center point and match result on the card
                image = cards.draw_results(image, cards_list[k])
                k += 1

        # Draw card contours on the image
        if (len(cards_list) != 0):
            temp_cnts = []
            for i in range(len(cards_list)):
                temp_cnts.append(cards_list[i].contour)
            cv2.drawContours(image, temp_cnts, -1, (255, 0, 0), 2)

    # Calculate framerate
    cv2.putText(image, "FPS: {0:.2f}".format(cv2.getTickFrequency() / (cv2.getTickCount() - t1)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    # Display the image
    cv2.imshow("Card Detector", image)

    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cv2.destroyAllWindows()
print("Done")
