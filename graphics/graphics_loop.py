# This process will read in graph information on stdin (piped from main loop) and paint pretty pictures based on my crappy math
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path += "/.."
sys.path.append(dir_path)
import data_structures
sys.path.remove(dir_path)

from PyQt6 import QtCore, QtGui, QtOpenGL,  QtOpenGLWidgets, QtWidgets
import OpenGL.GL as gl
from OpenGL import GLU

import numpy as np

import time
import threading
import re
import math

# Display extends a QGLWidget and will be what OpenGL draws everything in
class Display(QtOpenGLWidgets.QOpenGLWidget):

    def __init__(self, parent = None, G = None):
            self.parent = parent
            QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
            self.G = G

    # I think this is called after the window is launched? not surer
    def initializeGL(self):

        gl.glClearColor(0, 0, 0, 1)
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
        node_size = .11782 
        # This is (in GL coords) how big each node is. I have no idea how to actually calc it, so this is just based
        # on the dimensions of my little board set up.

        # This is for proof of concept. We will need to come back in here and do a bunch of
        # Linear Algebra to actually get something that is useable

        if(G.tag_node_dict[0].posvec is None or 
           G.tag_node_dict[1].posvec is None or
           G.tag_node_dict[2].posvec is None ): 
            #print("Not all tags have positions yet, passing")
            self.drawCalib() 
            return;
        self.drawCalib()        
        max_x = G.tag_node_dict[1].posvec[0] #+ (G.tag_node_dict[1].posvec[0] - min_x) * node_size
        min_x = G.tag_node_dict[0].posvec[0] #+ (G.tag_node_dict[1].posvec[0] - max_x) * node_size
        
        max_y = G.tag_node_dict[1].posvec[1] #+ (G.tag_node_dict[1].posvec[1] - min_y) * node_size * self.aspect
        min_y = G.tag_node_dict[2].posvec[1] #+ (G.tag_node_dict[1].posvec[1] - max_y) * node_size * self.aspect

        
        # Draw all the edges!
        for i in G.tag_edge_dict:
            e = G.tag_edge_dict[i]
            if(e.source_tracking_id not in G.tag_node_dict or
               e.sink_tracking_id not in G.tag_node_dict):
                print(e.source_tracking_id, "->", e.sink_tracking_id, " not in G.tag_node_dict")
                continue
            
            source = G.tag_node_dict[e.source_tracking_id]
            sourcex = source.posvec[0]
            sourcey = source.posvec[1]
            
            sink = G.tag_node_dict[e.sink_tracking_id]
            sinkx = sink.posvec[0]
            sinky = sink.posvec[1]

            gl.glLineWidth(20)
            gl.glColor(1,1,1)
            gl.glBegin(gl.GL_LINES)
            gl.glVertex2f( 2*(sourcex - min_x)/(max_x-min_x) - 1, 2 * (sourcey - min_y)/(max_y - min_y) - 1)
            gl.glVertex2f( 2*(sinkx  - min_x)/(max_x-min_x) -1, 2 * (sinky - min_y)/(max_y - min_y) - 1)
            gl.glEnd()

    
        gl.glFlush()



        # Draw all the nodes!
        for i in G.tag_node_dict:
            n = G.tag_node_dict[i]
            nx = n.posvec[0]
            ny = n.posvec[1]

            # Set color of polygon based on node_type
            if n.node_type == "Calibration":
                gl.glColor(1,.5,.5)
                # Draws some squares!
                # Again, not remotely good. We'll have to figure out exactly what to take from posvec and rotvec
                gl.glBegin(gl.GL_QUADS)
                gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1, 2*(ny - min_y)/(max_y - min_y) - 1 )
                gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 + node_size, 2*(ny - min_y)/(max_y - min_y) - 1 )
                gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 + node_size, 2*(ny - min_y)/(max_y - min_y) - 1 + node_size * self.aspect)
                gl.glVertex2f( 2*(nx - min_x)/(max_x - min_x) - 1 , 2 *(ny - min_y)/(max_y - min_y) - 1 + node_size * self.aspect )
                gl.glEnd()

            else: # For now, if not a calib node, it will draw an orange circle around the node.
                gl.glColor(1, 133/255, 0)
                gl.glBegin(gl.GL_POLYGON)
                xpos = 2*(nx - min_x)/(max_x - min_x) - 1
                ypos =  2*(ny - min_y)/(max_y - min_y) - 1 
                verts = 100
                for i in range(verts):
                    gl.glColor(1, (180 - abs(i - 50) ) / 255, 2 * (50 - abs(i - 50) ) / 255 )
                    gl.glVertex2f( xpos + math.cos(2 * math.pi * i / verts) * node_size, ypos + math.sin(2 * math.pi * i / verts) * node_size * self.aspect)  
                gl.glEnd() 

    def drawCalib(self):
        width = 1280
        height = 720
        node_size = .11782 
 
        # Draws calibration corners:
        gl.glColor(1,.1,.1)
        # Top left
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( -1, 1)
        gl.glVertex2f(-1 + node_size, 1)
        gl.glVertex2f( -1 + node_size, 1 - node_size * self.aspect) 
        gl.glVertex2f(-1, 1 - node_size * self.aspect)
        gl.glEnd()
        # Top right
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( 1, 1)
        gl.glVertex2f(1 - node_size, 1)
        gl.glVertex2f(1 - node_size, 1 - node_size * self.aspect) 
        gl.glVertex2f(1, 1 - node_size * self.aspect)
        gl.glEnd()
        # Bottom right
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( 1, -1)
        gl.glVertex2f(1 - node_size, -1)
        gl.glVertex2f(1 - node_size, -1 + node_size * self.aspect) 
        gl.glVertex2f(1, -1 + node_size * self.aspect)
        gl.glEnd()



# Not even gonna pretend like I understand Qt stuff or want to
# This is just the main window. Took this stuff from a tutorial
# https://nrotella.github.io/journal/first-steps-python-qt-opengl.html
class DisplayWindow(QtWidgets.QMainWindow):

    def __init__(self, G):
        QtWidgets.QMainWindow.__init__(self)   

        # Sets all the window stuff
        self.resize(1280, int(1280 / 1.22535))
        self.setWindowTitle('XR4XAI')

        # Sets the dsiplay class  to be the main object
        display = Display(self, G)
        self.setCentralWidget(display)
        
        # Adds a timer that refreshes the display every half second
        timer = QtCore.QTimer(self)
        timer.setInterval(500)   # period, in milliseconds
        timer.timeout.connect(display.paintGL)
        timer.start()


# Start display will create all the things we need for window/opengl
# and then launch
def start_display(G):
    app = QtWidgets.QApplication(sys.argv)
    print(G)
    win = DisplayWindow(G)
    win.show()

    app.exec()

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

    # Creates test edge set for demo:
    G.tag_edge_dict[0] = data_structures.Edge(source_tracking_id = 3, sink_tracking_id = 4)    
    G.tag_edge_dict[1] = data_structures.Edge(source_tracking_id = 4, sink_tracking_id = 5)
    G.tag_edge_dict[2] = data_structures.Edge(source_tracking_id = 5, sink_tracking_id = 3)
 

    update_thread = threading.Thread(target=update_graph, args = (G,) )
    update_thread.start()

    start_display(G)
    update_thread.join()
