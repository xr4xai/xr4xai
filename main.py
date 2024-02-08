import sys

from tracking import track_all
from graphics import start_graphics
import data_structures

import threading

import time
import cv2
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication

def gui(gui_dict):

    while True:
        cv2.imshow('frame', gui_dict['frame'])
        #gui_dict['view'].show()
        G.print_tags()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    

if __name__ == "__main__":

    
    G = data_structures.Graph()
    G.tag_node_dict[0] = data_structures.Node(tracking_id = 0, node_type="Calibration")
    G.tag_node_dict[1] = data_structures.Node(tracking_id = 1, node_type="Calibration")
    G.tag_node_dict[2] = data_structures.Node(tracking_id = 2, node_type="Calibration")


    gui_dict = {}

    # inits Qt window 
    print("Hand track info in green, tags in cyan")


    tracking_thread = threading.Thread(target=track_all.track, args=(G,gui_dict), group=None )
    drawing_thread = threading.Thread(target=start_graphics.parent, args=(), group=None )

    tracking_thread.start()
    drawing_thread.start()
    
    time.sleep(5)

    gui(gui_dict)

    tracking_thread.join()
    drawing_thread.join()
