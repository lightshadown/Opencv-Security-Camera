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
default_port = 7000

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
    
def save():
    log("save function")
    global outputFrame, lock
    saving_XVID = False
    saving_MP4G = False
    saving_X264 = False
    codec = False
    
    archivo = 'camera_' + datetime.now().strftime("%d-%m-%Y_%I-%M_%p") + '.mp4'
    camera = cap.isOpened()
    
    try:   #XVID saving
        videocodec = cv2.VideoWriter_fourcc('X','V','I','D')    #XVID 
        salida = cv2.VideoWriter(archivo, videocodec, 32.0,(1920,1080) )  #(int(cap.get(3)), int((cap.get(4)))))
        codec = salida.isOpened()
      #Check if the camera is open and the codec is working
        if ((camera == True) & (codec == True)):
            print('Camera and video codec properly loaded, XVID')
            log('Camera and video codec properly loaded, XVID')
        else:   
            salida.release()
            del videocodec
            try:    #mp4v saving
                videocodec = cv2.VideoWriter_fourcc('m','p','4','v')     # mp4v codec  
                salida = cv2.VideoWriter(archivo, videocodec, 32.0,(1920,1080) )  #(int(cap.get(3)), int((cap.get(4)))))
                codec = salida.isOpened()
                if ((camera == True) & (codec == True)):
                    print('Camera and video codec properly loaded, mp4v')
                    log('Camera and video codec properly loaded, mp4v')
                else:
                    salida.release()
                    del videocodec
                    try:  #H.264 saving
                        videocodec = cv2.VideoWriter_fourcc('a','v','c','1')    # H.264 codec works but need to erase or create a new file first
                        salida = cv2.VideoWriter(archivo, videocodec, 32.0,(1920,1080) )  #(int(cap.get(3)), int((cap.get(4)))))
                        codec = salida.isOpened()
                        if ((camera == True) & (codec == True)):
                            print('Camera and video codec properly loaded, h.264')
                            log('Camera and video codec properly loaded, h.264')
                    except:
                        pass
            except:
                pass        
            
        while ((cap.isOpened()) & (codec == True)):  # only saves the files if the camera and codec are loaded correctly
            with lock:
                if outputFrame is None:
                    continue
                width = outputFrame.shape[1]       # retrieve the width of the frame
                #flipFrame = cv2.flip(outputFrame, -1)   #makes sure the frame is fliped
                fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                # set the date on the current frame
                cv2.putText(outputFrame, fecha,(14, outputFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
            
                if width != 1920:       # resizes and write the frame to the video file
                    writeFrame = cv2.resize(outputFrame, (1920,1080), interpolation=cv2.INTER_AREA)
                    salida.write(writeFrame)
                else:
                    log('frame size dont match, cannot create video file')
        salida.release()
        log('video file created succesfully')       
    except:
        log("not working")
    # #mp4v saving
    # try:
    #     videocodec = cv2.VideoWriter_fourcc('m','p','4','v')     # mp4v codec  
    #     salida = cv2.VideoWriter(archivo, videocodec, 32.0,(1920,1080) )  #(int(cap.get(3)), int((cap.get(4)))))
    #     codec = salida.isOpened()
    #     if ((camera == True) & (codec == True) & (saving_XVID == False) &(saving_X264 == False) ):
    #         print('Camera and video codec properly loaded')
    #         log('Camera and video codec properly loaded')
    #         saving_MP4G = True
    #         while ((cap.isOpened()) & (codec == True)):  # only saves the files if the camera and codec are loaded correctly
    #             with lock:
    #                 if outputFrame is None:
    #                     continue
    #                 width = outputFrame.shape[1]       # retrieve the width of the frame
    #                 #flipFrame = cv2.flip(outputFrame, -1)   #makes sure the frame is fliped
    #                 fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    #                 # set the date on the current frame
    #                 cv2.putText(outputFrame, fecha,(14, outputFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
                
    #                 if width != 1920:       # resizes and write the frame to the video file
    #                     writeFrame = cv2.resize(outputFrame, (1920,1080), interpolation=cv2.INTER_AREA)
    #                     salida.write(writeFrame)
    #                 else:
    #                     log('frame size dont match, cannot create video file')
    #         salida.release()
    #         log('video file created succesfully')      
    # except:
    #     pass    
    # # h.264 saving
    # try:    
    #     videocodec = cv2.VideoWriter_fourcc('a','v','c','1')    # H.264 codec works but need to erase or create a new file first
    #     salida = cv2.VideoWriter(archivo, videocodec, 32.0,(1920,1080) )  #(int(cap.get(3)), int((cap.get(4)))))
    #     codec = salida.isOpened()
    #     if ((camera == True) & (codec == True) & (saving_MP4G == False) & (saving_XVID == False)):
    #         print('Camera and video codec properly loaded, H.264')
    #         log('Camera and video codec properly loaded, H.264')
    #         saving_X264 = True
    #         while ((cap.isOpened()) & (codec == True)):  # only saves the files if the camera and codec are loaded correctly
    #             with lock:
    #                 if outputFrame is None:
    #                     continue
    #                 width = outputFrame.shape[1]       # retrieve the width of the frame
    #                 #flipFrame = cv2.flip(outputFrame, -1)   #makes sure the frame is fliped
    #                 fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    #                 # set the date on the current frame
    #                 cv2.putText(outputFrame, fecha,(14, outputFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
                
    #                 if width != 1920:       # resizes and write the frame to the video file
    #                     writeFrame = cv2.resize(outputFrame, (1920,1080), interpolation=cv2.INTER_AREA)
    #                     salida.write(writeFrame)
    #                 else:
    #                     log('frame size dont match, cannot create video file')
    #         salida.release()
    #         log('video file created succesfully')         
    # except:
    #     log('not working')
    finally:
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


def detect(framesNum):   # make a call to out class and pass the frames to be weighted
    global outputFrame, lock#, vs
    md = singleModDetec(peso=0.1)
    total =0
    try:
        while True:
            ret, frame = cap.read()  # read the actual frame using Opencv
            #frame = vs.read()   # read the actual frame using Flask
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
    except:
        log('nothing to detect')    
 
 
def encode(ip):
    log("encode function")
    global outputFrame, lock

    if cap.isOpened() == True:    
        log('broadcasting to: ' + str(ip) + '  ---  Client no: ' + str(clientNumber) ) 
    if not cap.isOpened():
        errorMsg = 'Cannot open the camera'
        yield errorMsg
        log('Cannot open the camera')
    try:
        while cap.isOpened() == True: #& (codec == True)):  # only saves the files if the camera and codec are loaded correctly
            with lock:
                if outputFrame is None:
                    continue
                
                #flipFrame = cv2.flip(outputFrame, -1)   #makes sure the frame is fliped
                fecha = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
                # set the date on the current frame
                cv2.putText(outputFrame, fecha,(14, outputFrame.shape[0]-15), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0,0,255), 1 )  
          
                (flag, saveimg) = cv2.imencode(".jpg", outputFrame)
                if not flag:
                    continue
            # yield do the actual broadcast of the image
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(saveimg) + b'\r\n')
    except:
        log('cannot encode and show image') 
    
def Flask_Server(host_ip, puerto, frame, detect):

    log("Flask server parser")
    #start thread for motion detection and saving video file    
    #### To do, use multiprocesisng pool instead of threads, to reduce work load
    #### To do, reduce gray image to 40% to reduce image analicis on compute function
    if detect == "true":
        t_detect = threading.Thread(target=detect, args= (frame,))
        t_detect.daemon = True
        t_detect.start()
    t_save = threading.Thread(target=save)
    t_save.daemon = True
    t_save.start()
    
    #start the app
    #app.run(host=default_host_ip, port=puerto, debug=False, threaded=True, use_reloader=False)  # default ip RPi and port
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
    ap.add_argument("-a", "--auto", required=False, help="Set default ip and port for device", action="store_true")
    arg = vars(ap.parse_args())
    
    if (arg["ip"]) and (arg["port"]):
        Flask_Server( arg["ip"], arg["port"], arg["frame_count"], arg["detect_move"])
    if (arg["auto"]) and ( (arg["ip"] == False) or (arg["port"] == False) ):
        Flask_Server(default_host_ip, default_port, 32, True)
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