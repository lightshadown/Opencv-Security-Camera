
Small program on how to use opencv for Security cameras, can work either on pcs or rpi

Version 0.1.2
    Removed
    --Removed automatic detection of videocodec, the codec and video file can be selected from the list
    Added
    --added argument for videocodec and file type, m4pv + avi by default for RPi3

Version 0.1.1
    Added
    --reduce size of analiced image to 60% in order to reduce cpu/ram usage

Version 0.1
    Fixed
    --Added, automatic detection of the videocodec the system allow, it can be either XVID, mp4v, or h.264
    --analiced images tend to stay on memory and use too much CPU, they are erased after used
    --Removed fliped image working with normal image
    --set argument for enable/disable detection
    --Fixed auto argument at start, now if no ip/port is provided would set the server to machines ip and port to 7000

    **Todo**
    
    --add centroids for movement detection
    --add auto start on rpi3
    --find a way to use the rpi as a standalone camera and make a wifi hotspot for insite access
    --check how to use holybro antena
    --check how to host a free landing page on the cloud
    --check how to set proper speed on divx files


*Overall info

-- Access the main camera and saves every frame to a file with the current date and time 
-- Creates an small log when the camera opens and close, also when theres any problem with the video writer object 
-- Installation, just add ffmpeg and opencv via pip install, nothing more is needed 
-- video codecs list https://gist.github.com/takuma7/44f9ecb028ff00e2132e
-- image on webbroser tutorial  https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/ 
-- use --ip 0.0.0.0 --port 7000 for standart local server 
-- in some cases opencv must be compiled from scracht, follow this tutorial 2021 https://www.youtube.com/watch?v=zmdAVkSFYkQ
-- in order to make the broadcast aviable you can leave no parameter at all for auto or set the ip/port parameter for and especific addres 


*Know issues

--If for some reason you use h264 and is not saving the file properly, its an error related with your GPU drivers