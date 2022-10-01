
Small program on how to use opencv for Security cameras, can work either on pcs or rpi

Version 0.1
    Fixed
    --Added, automatic detection of the videocodec the system allow, it can be either XVID, mg4p, or h.264
    --analiced images tend to stay on memory and use too much CPU, they are erased after used
    --Removed fliped image working with normal image
    --set argument for enable/disable detection

    **Todo**
    --reduce size of analiced image to reduce cpu/ram usage
    --add centroids for movement detection


*Overall info

-- Access the main camera and saves every frame to an mp4 file with the current date and time \n
-- Creates an small log when the camera opens and close, also when theres any problem with the video writer object \n
-- Installation, just add ffmpeg and opencv via pip install, nothing more is needed \n
-- video codecs list https://gist.github.com/takuma7/44f9ecb028ff00e2132e \n
-- image on webbroser tutorial  https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/ \n
-- use --ip 0.0.0.0 --port 8000 for standart local server \n
-- in some cases opencv must be compiled from scracht, follow this tutorial 2021 https://www.youtube.com/watch?v=zmdAVkSFYkQ \n
-- in order to make the broadcast aviable the --ip parameter must be the Rpi ips \n