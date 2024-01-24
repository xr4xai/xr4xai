import os 
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

import aruco_tracker
import hand_tracker

sys.path.remove(dir_path)

import cv2
import cv2.aruco as aruco

def track(G = None):
    cap = cv2.VideoCapture(0)

    ret, mtx, dist, rvecs, tvecs = aruco_tracker.calib(cap)

    tracker = hand_tracker.handTracker()

    frames_counted = 0
    while True:
        
        ret, frame = cap.read()
        
        hand_tracker.track_hands(frame, tracker)
        aruco_tracker.track_tags(frame, ret, mtx, dist, rvecs, tvecs, G)
        
        cv2.imshow('frame',frame)

        # Print updates every five frames
        G.print_tags()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    track()
