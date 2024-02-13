# This process will read in graph information on stdin (piped from main loop) and paint pretty pictures based on my crappy math
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path += "/.."
sys.path.append(dir_path)
import data_structures
sys.path.remove(dir_path)

from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets
import OpenGL.GL as gl
from OpenGL import GLU

import numpy as np

import time
import threading
import re

# Display extends a QGLWidget and will be what OpenGL draws everything in
class Display(QtOpenGL.QGLWidget):

    def __init__(self, parent = None, G = None):
            self.parent = parent
            QtOpenGL.QGLWidget.__init__(self, parent)
            self.G = G

    # I think this is called after the window is launched? not surer
    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 0))
        #gl.glEnable(gl.GL_DEPTH_TEST

    # changes some things on resize
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glLoadIdentity()
        self.aspect = width / float(height)

    # Called everytime updateGL happens. Draws everything to the screen
    def paintGL(self):
        #gl.glColor(0,0,0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT )#| gl.GL_DEPTH_BUFFER_BIT)
        #gl.glLoadIdentity();
        
        #gl.glTranslatef(0,0,-4.0)

        width = 1280
        height = 720
        node_size = .5

        # This is for proof of concept. We will need to come back in here and do a bunch of
        # Linear Algebra to actually get something that is useable

        if(G.tag_node_dict[0].posvec is None or 
           G.tag_node_dict[1].posvec is None or
           G.tag_node_dict[2].posvec is None ): 
            print("Not all tags have positions yet, passing")
            return;
        
        min_x = G.tag_node_dict[0].posvec[0]
        max_x = G.tag_node_dict[1].posvec[0]
        min_y = G.tag_node_dict[2].posvec[1]
        max_y = G.tag_node_dict[1].posvec[1]

        
        for i in G.tag_node_dict:
            nx = G.tag_node_dict[i].posvec[0]
            ny = G.tag_node_dict[i].posvec[1]

            # Set color of polygon based on node_type
            if G.tag_node_dict[i].node_type == "Calibration":
                gl.glColor(1,.5,.5)
            else:
                gl.glColor(.5, 1, 1)
            
            # Draws some squares!
            # Again, not remotely good. We'll have to figure out exactly what to take from posvec and rotvec
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1, 2*(ny - min_y)/(max_y - min_y) - 1 )
            gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 + node_size, 2*(ny - min_y)/(max_y - min_y) - 1 )
            gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 + node_size, 2*(ny - min_y)/(max_y - min_y) - 1 + node_size * self.aspect)
            gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 , 2 *(ny - min_y)/(max_y - min_y) - 1 + node_size * self.aspect )
            gl.glEnd()

        gl.glFlush()
        print("Qt updated")




# Not even gonna pretend like I understand Qt stuff or want to
# This is just the main window. Took this stuff from a tutorial
# https://nrotella.github.io/journal/first-steps-python-qt-opengl.html
class DisplayWindow(QtWidgets.QMainWindow):

    def __init__(self, G):
        QtWidgets.QMainWindow.__init__(self)   

        # Sets all the window stuff
        self.resize(1280, 720)
        self.setWindowTitle('XR4XAI')

        # Sets the dsiplay class  to be the main object
        display = Display(self, G)
        self.setCentralWidget(display)
        
        # Adds a timer that refreshes the display every half second
        timer = QtCore.QTimer(self)
        timer.setInterval(500)   # period, in milliseconds
        timer.timeout.connect(display.updateGL)
        timer.start()


# Start display will create all the things we need for window/opengl
# and then launch
def start_display(G):
    app = QtWidgets.QApplication(sys.argv)
    print(G)
    win = DisplayWindow(G)
    win.show()

    app.exec_()

# Pulls lines from stdin and updates graph structure
def update_graph(G):
    for line in sys.stdin:
        if("Track" in line):
            #   Tracking ID:  2   SNN ID:       -1   Node type:    Calibration   Position:     None   Rotation:     None
            l = line.split('#')[1:]
            print(l)    
            n = data_structures.Node()
            n.tracking_id = int(l[0])
            n.snn_id = int(l[1])
            n.node_type = l[2]
            
            if("None" in l[3]):
                n.posvec = None
            else:
                n.posvec = [ float( x.lstrip('[').rstrip(']') ) for x in l[3].split() if x.lstrip('[').rstrip(']') != '' ] 

            if("None" in l[4]):
                n.rotvec = None
            else:
                n.rotvec = [ float(x.lstrip('[').rstrip(']') ) for x in l[4].split() if x.lstrip('[').rstrip(']') != '' ]

            G.tag_node_dict[n.tracking_id] = n
            G.touched = True
            G.print_tags()


# Spins up a therad to constantly update graph and launches window
if __name__ == "__main__":

    G = data_structures.Graph()
    G.tag_node_dict[0] = data_structures.Node(tracking_id = 0, node_type="Calibration")
    G.tag_node_dict[1] = data_structures.Node(tracking_id = 1, node_type="Calibration")
    G.tag_node_dict[2] = data_structures.Node(tracking_id = 2, node_type="Calibration")


    update_thread = threading.Thread(target=update_graph, args = (G,) )
    update_thread.start()

    start_display(G)
    update_thread.join()
