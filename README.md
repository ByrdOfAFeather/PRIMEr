<h1 align="center"> PRIMEr </h1>
Tar heel gameplay is a tool built at UNC-Chapel Hill by Gary Bishop to allow anyone to create game like experiences with
already existing gameplay footage. These are meant to be played by people with learning disabilities as they simplify the 
game immensely. 
<br><br>


PRIMEr is a "primer" of sorts for this website, listed <a href="https://www.tarheelgameplay.org">here</a>. This means that it takes in 
videos of gameplay and "prepares" them to be played like video games. It does this by asking a user for "actions" which represent
gameplay moments in the video. Such as moving, attacking, or jumping. It then scans the video with these examples to find all gameplay
points in the video. Once a list is built containing timepoints, an editor preforms the necessary JSON formatting to 
allow the video to be inserted into the website. <br><br>

This project's main focus is making the process of adding videos easier for the user adding them. As of now 
the current interface requires manual insertions of gameplay points across the entire video, a long and tedious process. 

<h1 align="center"> Building TemplateScanners </h1>

This project relies on another library, TemplateScanners, written in C++ with bindings for Python. This is done to take full advantage
of multithreading. This library can be found [here](https://github.com/ByrdOfAFeather/TemplateScanners).

The process of building the template scanner module from the provided C++ code is fairly straightforward. It is highly 
recommended that this is built using linux as the build process with windows is significantly more complex, however, it 
has been confirmed to work on windows.

First install the following C++ modules and ensure their path variables are set: <br> 
[OpenCV2 4.1](https://github.com/opencv/opencv/archive/4.0.1.zip) || [Install Instructions](https://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html)
<br>
Note that you also will need python-dev (The libraries for python-dev should be installed already with python on windows
but need to be acquired separately on linux.)
<br>
[Boost/Boost::Python install instructions Linux](https://www.boost.org/doc/libs/1_61_0/more/getting_started/unix-variants.html)
<br>
[Boost/Boost::Python install instructions Windows](https://www.boost.org/doc/libs/1_69_0/more/getting_started/windows.html)
<br>
<br>
Ensure that Cmake is installed with version >= 3.12. From there build the .so file by invoking cmake in the TemplateScanners
directory. Note that on windows the extension should be .pyd. Move the output file, either .pyd or .so into your python's 
DLLs or site-packages folder. On Windows you may need to include the following .dlls if they are unable to be detected in the path: <br>
(the ..... are used to indicate build information that is specific to the user) <br>
boost_python......dll <br>
opencv_core401.dll <br>
opencv_imgcodecs401.dll <br>
opencv_imgproc401.dll <br>
opencv_videoio401.dll <br>

Unfortunately no pre-compiled libraries exist yet so this process must be followed in order to run the program. If unable to complete this, 
it's possible to download an outdated version of the TemplateScanners library written in Python from this [commit](https://github.com/ByrdOfAFeather/PRIMEr/blob/c41b9e8359e2cd9563f137b0cb3c7415c7b3f385/VideoProcessing/TemplateScanners.py). However, this is 
not going to be updated and will most likely fail to work with the current api without significant modification.

<h1 align="center"> Results </h1>

### <a href="tarheelgameplay.org/play/?key=dominic-juliet-command">3D Sonic</a>

![Example of sonic gameplay](https://media.giphy.com/media/wsWQnZRvp0luT0fHzo/giphy.gif)

### <a href="https://tarheelgameplay.org/play/?key=temple-eric-powder">Mega Man</a>

![Example of MegaMan gameplay](https://media.giphy.com/media/g0mKmZLhRKwD5jvpUi/giphy.gif)

Punishment Examples: <br>
[Comparison Without Punishment ScannerV2](https://tarheelgameplay.org/play/?key=fiber-velvet-crater) <br>
[Comparison With Punishment ScannerV2](https://tarheelgameplay.org/play/?key=list-ticket-solid)
<br><br>
[Another Punishment Example ScannerV2](https://tarheelgameplay.org/play/?key=laser-radio-lucas)
<br><br>
[HD Video Example](https://tarheelgameplay.org/play/?key=turtle-before-mask)
<br><br>
[Transformers Example](https://tarheelgameplay.org/play/?key=manila-bonjour-game)
<h1 align="center"> Built With </h1>

openCV: https://github.com/opencv/opencv

flask: https://github.com/pallets/flask

flask-REST: https://github.com/flask-restful/flask-restful 

flask-CORS: https://github.com/corydolphin/flask-cors

Boost: https://www.boost.org


<h1 align="center"> Video Sources </h1>

Mario (NES): https://www.youtube.com/watch?v=rLl9XBg7wSs

Garfield (Famicom): https://www.youtube.com/watch?v=6JxeHtXmJ9s

FullMetal Alchemist (DS): https://www.youtube.com/watch?v=QxSl2XYw1jw

Megaman 2 (NES): https://www.youtube.com/watch?v=vuJ8Qr-3_zg

Transformers (NES): https://www.youtube.com/watch?v=uWjmkk5H9PE

