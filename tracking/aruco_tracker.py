"""
Framework   : OpenCV Aruco
Description : Calibration of camera and using that for finding pose of multiple markers
Status      : Working
References  :
    1) https://docs.opencv.org/3.4.0/d5/dae/tutorial_aruco_detection.html
    2) https://docs.opencv.org/3.4.3/dc/dbb/tutorial_py_calibration.html
    3) https://docs.opencv.org/3.1.0/d5/dae/tutorial_aruco_detection.html
"""

import numpy as np
import cv2
import cv2.aruco as aruco
import glob

import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(dir_path + "/..")
import data_structures

def calib(cap):

    print('\033[96m', "Starting calib", '\033[0m')

    ####---------------------- CALIBRATION ---------------------------
    # termination criteria for the iterative algorithm
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    # checkerboard of size (7 x 6) is used
    objp = np.zeros((6*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

    # arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    # iterating through all calibration images
    # in the folder
    images = glob.glob(dir_path + '/calib_images/checkerboard/*.jpg')

    for fname in images:

        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # find the chess board (calibration pattern) corners
        ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
    
        # if calibration pattern is found, add object points,
        # image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            # Refine the corners of the detected corners
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)

    print('\033[96m', "Aruco tracker initialized and callibrated", '\033[0m')
    return cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

 

    ###------------------ ARUCO TRACKER ---------------------------
    
def track_tags(frame, ret, mtx, dist, rvecs, tvecs, G):
    #if ret returns false, there is likely a problem with the webcam/camera.
    #In that case uncomment the below line, which will replace the empty frame 
    #with a test image used in the opencv docs for aruco at https://www.docs.opencv.org/4.5.3/singlemarkersoriginal.jpg
    # frame = cv2.imread('./images/test image.jpg') 

    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # set dictionary size depending on the aruco marker selected
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_100)

    # detector parameters can be set here (List of detection parameters[3])
    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshConstant = 10
    
    detector = aruco.ArucoDetector(aruco_dict,  parameters)

    # lists of ids and the corners belonging to each id
    corners, ids, rejectedImgPoints = detector.detectMarkers(frame)

    # font for displaying text (below)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # check if the ids list is not empty
    # if no check is added the code will crash
    if np.all(ids != None):

        # estimate pose of each marker and return the values
        # rvet and tvec-different from camera coefficients
        rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
        #(rvec-tvec).any() # get rid of that nasty numpy value array error
        

        for i in range(0, ids.size):
            # draw axis for the aruco markers
            cv2.drawFrameAxes(frame, mtx, dist, rvec[i], tvec[i], 0.1)
            
            # TODO: Put all of the Graph structures inside a mutex, because at present
            #       there will definitely be race conidtions.

            if(ids[i][0] in G.tag_node_dict):
                # If we find this ID, its assigned to a node, so we need only update its position
                G.tag_node_dict[ids[i][0]].posvec = tvec[i][0] # no idea why the nest the arrays like this
                G.tag_node_dict[ids[i][0]].rotvec = rvec[i][0]
            else:
                # Else, we will have to now check the SNN list.
                if(len(G.tag_node_dict) < len(G.snn_node_dict)):
                    # If we're here, theres something inside the SNN list that is not inside the tag list
                    # So the user is likely sticking a node on the board they want to track
                    # We first see if this is in the SNN dict
                    if(ids[i][0] in G.snn_node_dict and G.snn_node_dict[ids[i][0]].tracking_id == -1):
                        #  The id corresponding to this tag is in the SNN map, and free in the tag map
                        #  we'll use that to try to keep things clean. Although this step is not needed.
                        #  It could help avoid O(n) but also n is gonna be like, 20 max, so its not a big
                        #  deal and it just kinda complicates things so maybe remove this part and just
                        #  search through the list to begin with. 
                        n = snn_node_dict[ids[i][0]]
                        n.tracking_id = ids[i][0]
                        n.posvec = tvec[i][0]
                        n.rotvec = rvec[i][0]
                        G.tag_node_dict[ids[i][0]] = n               
                    
                    else:
                        # Now we incur O(n)
                        for free in G.snn_node_dict:
                            if(G.snn_node_dict[free].tracking_id == -1):
                                # Found a free SNN list only node. Set it and add it and break
                                n = G.snn_node_dict[free]
                                n.tracking_id = ids[i][0]
                                n.posvec = tvec[i][0]
                                n.rotvec = rvec[i][0]
                                G.tag_node_dict[ids[i][0]] = n
                                break

                else:
                    # Otherwise, we assume we have to create a new node object.
                    # The SNN thread will claim this spot later if it needs it
                    n = data_structures.Node(tracking_id = ids[i][0])
                    n.posvec = tvec[i][0]
                    n.rotvec = rvec[i][0]
                    G.tag_node_dict[ids[i][0]] = n

            G.touched = True

        

        # draw a square around the markers
        aruco.drawDetectedMarkers(frame, corners)


        # code to show ids of the marker found
        strg = ''
        for i in range(0, ids.size):
            strg += str(ids[i][0])+', '

        cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)


    else:
        # code to show 'No Ids' when no markers are found
        cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)



