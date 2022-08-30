# video codecs list https://gist.github.com/takuma7/44f9ecb028ff00e2132e
# image on webbroser  https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

from sys import flags
import cv2
import numpy as np
from datetime import datetime
from DetectObject import singleModDetec
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import imutils
import argparse
import time

outputFrame = None
lock = threading.Lock()  # thread safe, avoid a thread read a frame thats been use by another thread

app = Flask(__name__)  #starts the flask object

# only one can be active at the same time
#vs = VideoStream(usePiCamera=1).start()   # use this one for Rpi camera module, only
vs = VideoStream(src=0).start()      # use this for usb camera

@app.route("/")   
def index():   # creates the webpage where i can see the images
    return render_template("index.html")


def detect(framesNum):   # make a call to out class and pass the frames to be weighted
    global outputFrame, lock, vs
    md = singleModDetec(peso=0.1)
    total =0
    
    while True:
        frame = vs.read()   # read the actual frame
        frame = imutils.resize(frame, width=400)   # recize the frame
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(7,7),0)
        fecha = datetime.now().strftime("%d-%m-%Y_%I-%M %p")
        cv2.putText(frame, fecha,(10, frame.shape[0]-10), cv2.FONT_HERSHEY_COMPLEX, 0.35, (0,0,255), 1 )   # set text on the procesed object
        
        if total > framesNum:
            motion = md.compute(gray)
            if motion is not None:  # get the tuple and unpack it, then set the rectangle where any motion is detected
                (umbral, (minx, miny, maxX, maxY)) = motion
                cv2.rectangle(frame, (minx, miny), (maxX, maxY), (0,0,255), 2) 
        
        md.update(gray)
        total += 1    
        
        with lock:    # makes thread safe
            outputFrame = frame.copy()
            
            
def encode_and_save():
    global outputFrame, lock
    
    archivo = 'camera_' + datetime.now().strftime("%d-%m-%Y_%I-%M %p") + '.mp4'
    while True:
        with lock:
            if outputFrame is None:
                continue
            #videocodec = cv2.VideoWriter_fourcc('a','v','c','1')    # H.264 codec works but need to erase or create a new file first
            #salida = cv2.VideoWriter(archivo, videocodec, 24.0, (320, 240) )#(int(cap.get(3)), int((cap.get(4)))))
            #salida.write(outputFrame)
            (flag, saveimg) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(saveimg) + b'\r\n')
        
    salida.release()

    
@app.route("/video_feed")
def video_feed():
    return Response(encode_and_save(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # arguments for command line
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True, help="ip of server")
    ap.add_argument("-o", "--port", type=int, required=True, help="port number for this server")
    ap.add_argument("-f", "--frame-count", type=int, default=32, help="number of Frames")
    arg = vars(ap.parse_args())
    
    #start thread for motion detection
    t = threading.Thread(target=detect, args= (arg["frame_count"] ,))
    t.daemon = True
    t.start()
    
    #start the app
    app.run(host=arg['ip'], port=arg["port"], debug=True, threaded=True, use_reloader=False)
#release video pointer
vs.stop()