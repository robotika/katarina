Katarina
=======

Parrot drone Bebop

* autonomous drone controlled via Python

For detail info see
http://robotika.cz/robots/katarina/

![Katarina Bebop Drone](http://robotika.cz/robots/katarina/katarina.jpg)

# Notes/Howto

First of all note, that this experimental project is *work in progress* and it
is your responsibility if you decide to use it without understanding the risks.
Inspiration and message codes are taken from official Parrot SDK:
https://github.com/ARDroneSDK3

The goal for Katarina repository is tha same as for Heidi
(https://github.com/robotika/heidi) ARDrone2 --- autonomous flying programmed
in Python. The code is developed and tested on laptop running Win7 and Python
2.7 but it should be easy to port it to other OS. Image processing uses OpenCV2
and NumPy libraries.

Code example:
```
drone = Bebop()
drone.takeoff()
drone.flyToAltitude(2.0)
drone.takePicture()
drone.land()
```

Surely the code becomes more complicated if you want to integrate video
processing or complex navigation. On the other hand it is relatively short so
you may read details "what is going on" ;-). Every run it logged and you should
be able to immediately replay it. See "bebop.py" file for example(s).

Warning! Autonomous flights sometimes turn bad ... and you need to stop the
drone ASAP. For my simple experiments landing is so far good choice what to do,
so as soon as I hit any key, the ManualControlException is raised and
alternative code is performed (typically combination of land() and
emergency() due to unlucky implementation of state machine on ARDrone3). This
means that the code above should be wrapped into try .. except
ManualControlException block.

The code evolved into several files:

* bebop.py --- this is the main file you need to import. The class Bebop
connects to the drone, contains up-to-date status variables and methods for
basic flight operations. There are several ""test"" demos, which follow the
experiments (and it will be probably moved to separate file).

* commands.py --- here you find list of some basic ARDrone3 commands
converting name into few bytes packet.

* navdata.py --- parsing of (not only) navigation data. The name was taken from
ARDrone2. You can use this script also for detail verbose dump of recorded
"navdata" log.

* video.py --- handing of parts of H264 video frames. Also serves as utility
  for video conversion and extraction of individual frames.

* play.py --- play video using OpenCV2 (uses video.py as conversion routine, if
  necessary).

* capdet.py --- two color Parrot cap detection experiment (reference colors are
  stored in cap-colors.txt).

* apyros folder --- logging tools, shared among several Python driven robots.
  This folder is planned be moved into separate repository.

* demo.py --- integration of image processing with flight control (work in
  progress)


# FAQ

Q: I recently succeed to launch demo.py but I've a question about the 
parameter "task" in some of your scripts, is there any list of task that 
i should use to launch these scripts ? Are this just a name given to the 
instance of the demo ?

A: The "task" parameter is dummy at the moment. It should be named rather
"comment", because this is the way how I mainly use it (it is automatically
stored in metalog file), i.e. testWithTakeoffInWindyCondition. The plan is
to use it for "task selection" in the future ...


Q: What is module "cvideo"?

A: "cvideo" is taken from Heidi/ARDrone2:
https://github.com/robotika/heidi/tree/master/cvideo
It is used for decoding H.264 encoded frames into numpy array used as image
in OpenCV2. OpenCV2 can open stream or file but I could not convince to read
several frames.


Q: What is the state of your work? Is every module finished?

A: The basic code in bebop.py, commands.py and navdata.py (+video.py) are
ready to use. It was tested under Windows 7/Python 2.7 and I am sure that in
particular https://github.com/robotika/katarina/blob/master/apyros/manual.py
will require revision for Linux and Mac OS.

The other modules are rather ""work in progress"", where the closest to
reasonable image multiprocessing is
https://github.com/robotika/katarina/blob/master/behaviors/navbox.py
(as example, the image processing algorithm needs some improvements).


Q: Does demo.py open video player?

A: No it should not. In reality I preffer rather watch/check the drone what
it is doing and AFTER review the video and processed images. Note, that demo.py
needs multiprocessing revision as mentioned in previous question.
For debugging OpenCV2 is used for display images.


Q: Can I get images from down-pointing camera?

A: As far as I know the answer is NO. Current API does not suppor it.
On the other hand you can select region of interest of forward looking camera by:
    drone.moveCamera( tilt=-100, pan=0 )


Q: I noticed that "drone.battery" always displays "None", did you get the same?

A: This means that there was no info packet with battery change status. I would try
to integrate ARCOMMANDS_ID_COMMON_SETTINGS_CMD_ALLSETTINGS, which should (?)
report "all settings" (including battery status?).


Q: I tried to use drone.flyToAltitude(3.0), but the drone does not fly to 3 meters. Why?

A: Please note, there is second parameter "timeout" with very low default value 3 seconds. So you
can write something like drone.flyToAltitude(3.0, timeout=20). Also note that the maximum
altitude is limited by drone settings.

