# video codecs list https://gist.github.com/takuma7/44f9ecb028ff00e2132e
# image on webbroser tutorial  https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
# use --ip 0.0.0.0 --port 8000 for standart local server
# in some cases opencv must be compiled from scracht, follow this tutorial 2021 https://www.youtube.com/watch?v=zmdAVkSFYkQ
# in order to make the broadcast aviable the --ip parameter must be the Rpi ips
# https://docs.python.org/3/library/multiprocessing.html

from ast import arg
import code
from concurrent.futures import thread
from crypt import methods
from pickle import TRUE
from sys import flags
import cv2
import numpy as np
from datetime import datetime
from DetectObject import singleModDetec
from imutils.video import VideoStream
from flask import Response
from flask import request
from flask import Flask
from flask import render_template
import threading
import imutils
import argparse
import socket
from contextlib import closing

#global variables
outputFrame = None
lock = threading.Lock()  # thread safe, avoid a thread read a frame thats been use by another thread
clientNumber = 0        #number of active clients
sock_listo = False
host = socket.gethostname()
default_host_ip = socket.gethostbyname(host)
default_port = 7500

#starts the flask object
app = Flask(__name__) 

# only one can be active at the same time
#vs = VideoStream(usePiCamera=1).start()   # Flask, use this one for Rpi camera module, only
#vs = VideoStream(src=0).start()            # Flask, use this for internal or usb camera
cap = cv2.VideoCapture(0)                  # OpenCV, start the camera

def checkPort():
    global sock_listo
    port = default_port
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        while sock_listo == False and port < 8001:
            if sock.connect_ex((default_host_ip, default_port)) == 0:
                sock_listo = True
                print("Actual port " + port)
                return port
            else:
                #print (port)
                sock_listo = False
                port += 1
        if port > 8000:
            return 0

def log(datatolog):  # log del servidor
    file = open("LogCamera.txt", "a")
    file.write("{0} -- {1}\n".format(datetime.now().strftime("%H:%M %d-%m-%Y"),datatolog))
    file.close()
    
def save(cc_type, file_type):  
    # by default is set to mp4v + avi for RPI, thats cc_type = 0 and file_type = 2
    global outputFrame, lock
    codec = False
    
    archivo = 'camera_' + datetime.now().strftime("%d-%m-%Y_%I-%M_%p") 
    camera = cap.isOpened()
    ext = ['.mp4', '.xvid', '.avi']
    videocc = ['mp4v', 'XVID', 'avc1', 'MJPG']
    archivo_salida = archivo + ext[2]
        # for Rpi mp4v + avi are compresed , XVID + avi are uncrompresed files
        # avc1(h264) have conflict behaviors on Rpi3
        # for macOs use avc1 + mp4
    try:
        print(archivo_salida)
        if (cap.get(3) != 1920) or (cap.get(4) != 1080):
            width = int(cap.get(3))
            height = int(cap.get(4))
            #print("size not match: " + str(width) + ', ' + str(height))
            log('size mismatch: ' + str(width) + ', ' + str(height))
            videocodec = cv2.VideoWriter_fourcc(*videocc[cc_type])     
            salida = cv2.VideoWriter(archivo_salida, videocodec, 24.0,(1920,1080))
            codec = salida.isOpened()
        else:
            width = int(cap.get(3))
            height = int(cap.get(4))
            print('width: ' + str(width) + ' Heght: ' + str(height))
            videocodec = cv2.VideoWriter_fourcc(*videocc[cc_type])   
            salida = cv2.VideoWriter(archivo_salida, videocodec, 24.0,(int(cap.get(3)), int(cap.get(4))))
            codec = salida.isOpened()
        #Check if the camera is open and the codec is working
        if ((camera == True) & (codec == True)):
            print('Camera and video codec properly loaded ' + str(videocc[cc_type])  +' + ' + str(ext[file_type]))
            log('Camera and video codec properly loaded, ' + str(videocc[cc_type]) +' + ' + str(ext[file_type]))        
        
        
        #Check if the camera is open and the codec is working                         
        if ((camera == True) & (codec == False)):
            print('camera working but unable to load video codec for saving video')
            log('camera working but unable to load video codec for saving video')
        if ((camera == False) & (codec == False)):
            print('Unable to load camera and video codec')
            log('Unable to load camera and video codec')
        if ((camera == False) & (codec == True)):
            print('Camera unable to load, but video codec loaded properly')
            log('Camera unable to load, but video codec loaded properly')
        
        while ((cap.isOpened()) & (codec == True)):  # only saves the files if the camera and codec are loaded correctly
            
            ret, frame = cap.read()  # read the actual frame using Opencv
            if ret ==False:
                continue
            else:
                outputFrame = frame.copy()
            
            with lock:
                if outputFrame is None:
                    continue
                width = outputFrame.shape[1]       # retrieve the width of the frame
                flipFrame = cv2.flip(outputFrame, 1)   #makes sure the frame is fliped
                fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                # set the date on the current frame
                cv2.putText(flipFrame, fecha,(14, flipFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
            
                if width != 1920:       # resizes and write the frame to the video file
                    rezisedFrame = cv2.resize(flipFrame, (1920,1080), interpolation=cv2.INTER_AREA)
                    salida.write(rezisedFrame)
                else:
                    salida.write(flipFrame)
                #else:
                #    log('frame size dont match, cannot create video file: ' + str(width))
                    
        salida.release()
        log('video file created succesfully')       
    except:
        log("not working")
                

def detect(framesNum):   # make a call to out class and pass the frames to be weighted
    global outputFrame, lock#, vs
    md = singleModDetec(peso=0.1)
    total =0
    try:
        while True:
            #ret, frame = cap.read()  # read the actual frame using Opencv
            #frame = vs.read()   # read the actual frame using Flask
            frame = outputFrame.copy()
            frame = imutils.resize(frame, width=400)   # recize the frame
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray,(7,7),0)
            
            if total > framesNum:
                motion = md.compute(gray)
                if motion is not None:  # get the tuple and unpack it, then set the rectangle where any motion is detected
                    (umbral, (minx, miny, maxX, maxY)) = motion
                    cv2.rectangle(frame, (minx, miny), (maxX, maxY), (0,0,255), 2) 
            
            md.update(gray)
            total += 1    
            frame = imutils.resize(frame, width=1080)
            
            with lock:    # makes thread safe
                outputFrame = frame.copy()
            del frame
    except:
        log('nothing to detect')    
 
 
def encode(ip):
    log("encode function")
    global outputFrame, lock

    if cap.isOpened() == True:    
        log('broadcasting to: ' + str(ip) + '  ---  Client no: ' + str(clientNumber) ) 
    if not cap.isOpened():
        log('Cannot open the camera')
    try:
        while cap.isOpened() == True: 
            with lock:
                if outputFrame is None:
                    continue
                
                flipFrame = cv2.flip(outputFrame, 1)   #makes sure the frame is fliped
                fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                # set the date on the current frame
                cv2.putText(flipFrame, fecha,(14, flipFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
          
                (flag, saveimg) = cv2.imencode(".jpg", flipFrame)
                if not flag:
                    continue
            # yield do the actual broadcast of the image
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(saveimg) + b'\r\n')
    except:
        log('cannot encode and show image') 
    
def Flask_Server(host_ip, puerto, frame, detect, cc,arch ):

    log("Flask server parser")
    #start thread for motion detection and saving video file    
    #### To do, use multiprocesisng pool instead of threads, to reduce work load
    #### To do, reduce gray image to 40% to reduce image analicis on compute function
    t_save = threading.Thread(target=save, args=(cc,arch))
    t_save.daemon = True
    t_save.start()
    if detect == "true":
        t_detect = threading.Thread(target=detect, args= (frame,))
        t_detect.daemon = True
        t_detect.start()
    
    #start the app
    app.run(host=host_ip, port=puerto, debug=False, threaded=True, use_reloader=False)


@app.route("/")   
def index():   # creates the webpage where i can see the images
    return render_template("index.html")


@app.route("/video_feed", methods=['POST', 'GET'])
def video_feed():
    global clientNumber
    clientNumber += 1

    ip = str(request.remote_addr)

    return Response(encode(ip), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    #arguments for command line
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False, help="ip of server")
    ap.add_argument("-o", "--port", type=int, required=False, help="port number for this server")
    ap.add_argument("-f", "--frame_count", type=int, default=32, help="number of Frames")
    ap.add_argument("-d", "--detect_move", required=False, help="Enable/Disable movement detection, true or false")
    ap.add_argument("-c", "--videocodec", required=False, help="video compresion can be mp4v, XVID, avc1, MJPG use a number")
    ap.add_argument("-e", "--file_ext", required=False, help="file extension can be mp4, xvid, avi, use a number")
    ap.add_argument("auto", nargs='?', default='True', help="Set default ip and port for device")  #, action="store_true")
    arg = vars(ap.parse_args())
    
    try:
        print(arg['auto'])
        if (arg["auto"] == 'True'):
            Flask_Server(default_host_ip, default_port, 32, 'False', 0,2 )
    except:
        if (arg["ip"]) and (arg["port"]):
            Flask_Server( arg["ip"], arg["port"], arg["frame_count"], arg["detect_move"], arg["videocodec"], arg["file"])
    # puerco = checkPort()
    # if sock_listo == True and not puerco == 0:
    #     log("starting server at " + str(arg["ip"]))
    #     Flask_Server( arg["ip"],puerco, arg["frame_count"], arg["detect_movement"])
    # else:
    #     print("unable to start flask server on " + str(arg["ip"]) +", using default host on " + str(default_host_ip))
    #     log("unable to start flask server at " + str(arg["ip"]))
    #     Flask_Server(default_host_ip, default_port, arg["frame_count"], arg["detect_movement"])
        
#release video pointer
    cap.release()

#vs.stop()