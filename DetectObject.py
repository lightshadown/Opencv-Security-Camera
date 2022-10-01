from concurrent.futures import thread
from tokenize import PseudoExtras
import numpy as np
import cv2
import imutils

class singleModDetec:
    def __init__(self, peso=0.5):   # initialize the background and weight of the image
        self.peso = peso   # Acumulated weight 
        self.bg = None
        
    def update(self, image):
        if self.bg is None:
            self.bg = image.copy().astype("float")  # starts by filling the background with the first frame of the image
            return
        cv2.accumulateWeighted(image, self.bg, self.peso) # start checkign the diference betwen the background and the new frame
        
    def compute(self, image, value=25):
        delta = cv2.absdiff(self.bg.astype("uint8"), image)  # total diference betwen background and frame
        umbral = cv2.threshold(delta, value, 255, cv2.THRESH_BINARY)[1]  # transform to threshold
        umbral = cv2.erode(umbral, None, iterations=2)       # erode and dilate to remove noise and defects on the image
        umbral = cv2.dilate(umbral, None, iterations=2)
        contornos = cv2.findContours(umbral.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE )  # find contourns of the treshold image
        contornos = imutils.grab_contours(contornos)   # grab the contourns of the image
        (minx, miny) = (np.inf, np.inf)       # here goes the coordinates for the bounding box
        (maxX, maxY) = (-np.inf, -np.inf)
        
        if len(contornos) == 0:  # if nothing found return none
            return None
        
        for c in contornos:  # populates coordinates on where the objects are found
            (x, y, w, h) = cv2.boundingRect(c)
            (minx, miny) = ( min(minx, x), min(miny, y) )
            (maxX, maxY) = ( max(maxX, x+w), max(maxY, y+h) )
    
        #Delete variables to avoid excessive workload on core
        del delta
        del umbral
        del contornos
        
        # returns a tuple of the treshold image and the coordinates on where was found movement
        return (umbral, (minx, miny, maxX, maxY))   