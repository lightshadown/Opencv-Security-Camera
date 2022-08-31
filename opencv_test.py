# opencv24-python-tutorials-readthedocs-io-en-stable.pdf en documentos/libros
#https://thedatafrog.com/en/articles/human-detection-video/
# check https://github.com/kkroening/ffmpeg-python
# video codecs list https://gist.github.com/takuma7/44f9ecb028ff00e2132e
# image on webbroser  https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

import cv2
import numpy as np
from datetime import datetime


def log(datatolog):  # log del servidor
    file = open("LogCamera.txt", "a")
    file.write("{0} -- {1}\n".format(datetime.now().strftime("%H:%M %d-%m-%Y"),datatolog))
    file.close()


def inc_brig(cuadro, value):
    hsv = cv2.cvtColor(cuadro, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim ] = 255
    v[v <= lim] += value
    #cv2.add(hsv[:,:,2], value, hsv[:,:,2])
    final_hsv = cv2.merge((h,s,v))
    cuadro = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return cuadro


def camera_works():
    status = False
    cap = cv2.VideoCapture(0)  # start the camera
    archivo = 'camera_' + datetime.now().strftime("%d-%m-%Y_%I-%M %p") + '.mp4'
    #videocodec = cv2.VideoWriter_fourcc('m','p','4','v')    # mp4v is for mp4 , but need ffmpeg compiled from scrach
    videocodec = cv2.VideoWriter_fourcc('a','v','c','1')    # H.264 codec works but need to erase or create a new file first
    salida = cv2.VideoWriter(archivo, videocodec, 24.0, (int(cap.get(3)), int(cap.get(4)) ) )#(int(cap.get(3)), int((cap.get(4)))))
    # write function that erases previous file because videowriter fails otherwise
    camera = cap.isOpened()
    codec = salida.isOpened()
    if ((camera == True) & (codec == False)):
        #camera = cap.isOpened()
        #codec = salida.isOpened()
        print('camera working but unable to load video codec for saving video')
        log('camera working but unable to load video codec for saving video')
    if ((camera == False) & (codec == False)):
        #camera = cap.isOpened()
        #codec = salida.isOpened()
        print('Unable to load camera and video codec')
        log('Unable to load camera and video codec')
    if ((camera == True) & (codec == True)):
        #camera = cap.isOpened()
        #codec = salida.isOpened()
        print('Camera and video codec properly loaded')
        log('Camera and video codec properly loaded')
    if ((camera == False) & (codec == True)):
        #camera = cap.isOpened()
        #codec = salida.isOpened()
        print('Camera unable to load, but video codec loaded properly')
        log('Camera unable to load, but video codec loaded properly')

    if cap.isOpened() == True:    
        log('Camera Open')
        while(cap.isOpened()):
            ret, frame = cap.read()
            
            if frame is None:
                print ('no frame')
            else:
                if ret == True:
                    frame = cv2.flip(frame, 1)
                    frame = inc_brig(frame, 30)            
                    #detect people
        #            boxes, weight = hog.detectMultiScale(frame, winStride=(8,8))
                    #return coordinates for people boxes
        #            boxes = np.array( [[x, y, x+w, y+h] for (x, y, w, h) in boxes ])
                    
        #            for (xA, yA, xB, yB) in boxes:
                        #display boxes in color picture
        #                cv2.rectangle(frame, (xA, yA), (xB, yB), (255,0,0), 2)
                    #frame = cv2.line(frame,(200,20),(511,511),(220,0,0),5)  # draw lines
                    #fuente = cv2.FONT_HERSHEY_COMPLEX
                    #cv2.putText(frame,'Prueba motherfucker', (300,90), fuente, 1, (255,255,255), 2, cv2.LINE_AA)
                    #frame = cv2.rectangle(frame, (300,100), (800,600), (200,0,0), 3)
                    salida.write(frame)     #write to file
                    #720,1280,3
                    cv2.imshow('Camara opencv', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
        cap.release()
        salida.release()
        cv2.destroyAllWindows()
        log('Camera close')

if __name__ == "__main__":
    camera_works()
