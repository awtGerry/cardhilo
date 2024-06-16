# Description: This file contains the data analysis functions for the card detector.
# The functions in this file are used to load the training data, preprocess the image,
# find and sort the contours of the cards, preprocess the cards,
# match the cards with the training data, and draw the results on the image.
# The main loop in main.py calls these functions to process the image captured from
# the ESP32-CAM and display the results on the screen.

class CardData:
    def __init__(self) -> None:
        self.card = None
        self.count = 0
        self.probs = []
