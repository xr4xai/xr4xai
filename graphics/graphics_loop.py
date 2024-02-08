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


class Display(QtOpenGL.QGLWidget):

    def __init__(self, parent = None, G = None):
            self.parent = parent
            QtOpenGL.QGLWidget.__init__(self, parent)

    def init_display(self):
        self.qglClearColor(QtGui.QColor(255, 0, 0))
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resize_display(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paint_display(self):
	    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

class DisplayWindow(QtWidgets.QMainWindow):

    def __init__(self, G):
        QtWidgets.QMainWindow.__init__(self)    # call the init for the parent class

        self.resize(300, 300)
        self.setWindowTitle('Hello OpenGL App')

        display = Display(self, G)
        self.setCentralWidget(display)

def start_display(G):
    app = QtWidgets.QApplication(sys.argv)
    print(G)
    win = DisplayWindow(G)
    win.show()

    app.exec()

def update_graph(G):
    for line in sys.stdin:
        print(line)


if __name__ == "__main__":
    print("how could a loving god cause so much pain?")
    bleh = input()
    print("From child: ",  bleh)

    G = data_structures.Graph()

    update_thread = threading.Thread(target=update_graph, args = (G,) )
    update_thread.start()

    start_display(G)
    update_thread.join()
   

"""
    width = 1280
    height = 720
    node_size = 100


    orange = QBrush(Qt.red)
    black = QBrush(Qt.black)

    # This is for proof of concept. We will need to come back in here and do a bunch of
    # Linear Algebra to actually get something that is useable
    while True:

        if(G.tag_node_dict[0].posvec is None or 
           G.tag_node_dict[1].posvec is None or
           G.tag_node_dict[2].posvec is None ): 
            time.sleep(1/15)
            print("Not all tags have positions yet, passing")
            continue
        min_x = G.tag_node_dict[0].posvec[0]
        max_x = G.tag_node_dict[1].posvec[0]
        min_y = G.tag_node_dict[1].posvec[1]
        max_y = G.tag_node_dict[2].posvec[1]

    
        for i in G.tag_node_dict:
            nx = G.tag_node_dict[i].posvec[0]
            ny = G.tag_node_dict[i].posvec[1]

            rect = QGraphicsRectItem( (nx - min_x)/(max_x - min_x) * width, (ny - min_y)/(max_y - min_y) * height, node_size, node_size)
            rect.setBrush(orange)
            gui_dict['scene'].addItem(rect)
            
        
        print("Qt updated")
        time.sleep(1/30)

"""
