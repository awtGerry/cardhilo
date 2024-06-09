# VideoStream.py
import cv2
import numpy as np
import urllib.request

class VideoStream:
    def __init__(self, src=0):
        self.stream = urllib.request.urlopen("http://192.168.100.124:81/stream")
        self.bytes = b''
        self.stopped = False

    def start(self):
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            self.bytes += self.stream.read(1024)
            a = self.bytes.find(b'\xff\xd8')
            b = self.bytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = self.bytes[a:b+2]
                self.bytes = self.bytes[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

    def read(self):
        a = self.bytes.find(b'\xff\xd8')
        b = self.bytes.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = self.bytes[a:b+2]
            self.bytes = self.bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            return img
        else:
            return None

    def stop(self):
        self.stopped = True
