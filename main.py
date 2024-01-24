from tracking import track_all
import data_structures
import graphics_loop

import threading

import time

if __name__ == "__main__":

    
    G = data_structures.Graph()
    G.tag_node_dict[0] = data_structures.Node(tracking_id = 0, node_type="Calibration")
    G.tag_node_dict[1] = data_structures.Node(tracking_id = 1, node_type="Calibration")
    G.tag_node_dict[2] = data_structures.Node(tracking_id = 2, node_type="Calibration")
    
    print("Hand track info in green, tags in cyan")
    
    tracking_thread = threading.Thread(track_all.track, args=(G,) )
    drawing_therad = threading.Thread(graphics_loop.projector_display, args=(G,) )

    tracking_thread.start()

    time.sleep(5)

    drawing_thread.start()

    tracking_thread.join()
    drawing_thread.join()
