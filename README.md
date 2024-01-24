# XR4XAI

### Jake Looney and Andrew Lay
### Sponsored by Dr. Sai Swaminathan, Dr. Jian Huang, and Dr. Catherine Schuman

## Aruco Tracking Install instructions
This code is supplied by njanirudh on Github, and edited.
It implements the aruco packages of OpenCV
Vist their [GitHub](https://github.com/njanirudh/Aruco_Tracker) to Star and clone it
To run it, you'll need to do:
```
pip3 install opencv-python
pip3 install opencv-contrib-python
```
My version for opencv-python is 4.8.1.78 and for opencv-python-contrib is also 4.8.1.78. To the extent that other versions work, I'm not sure. Also not entirely sure if opencv-contirb-python does anything, thats just what the people who made that GitHub said to do. 
You can test it by running `python3 ArucoTracker/aruco_tracker.py` 

## Hand Tracking Install instructions
The hand tracker requires mediapipe. Install it:
```
pip3 install mediapipe
```
You might also have to do some wacky nonsense to get it actually build. This is availble form this [StackOverflow question](https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal)

user19266443 prescribes:
```
Follow these steps:

    Install the latest protobuf version (in my case is 4.21.1)

    pip install --upgrade protobuf

    Copy builder.py from .../Lib/site-packages/google/protobuf/internal to another folder on your computer (let's say 'Documents')
    Install a protobuf version that is compatible with your project (for me 3.19.4)

    pip install protobuf==3.19.4

    Copy builder.py from (let's say 'Documents') to Lib/site-packages/google/protobuf/internal
    Run your code

```
I'm running mediapipe version 0.9.3.0

The tracker is from [this article](https://www.section.io/engineering-education/creating-a-hand-tracking-module/) although will probably see some more editing. 

## TENNLab Neuromorphic framework installation

Still working on this




