"""
This file implements a Graphics View for the GUI, and the main function that will 
create and run that graphics view. it utilizes qt_node and qt_edge files.
It also utilizes the snn directory to get infromation from simualted networks. (i.e. make sure your sourced into pyframework)
"""


import sys
from typing import Iterable
from PyQt6.QtWidgets import (
    QGraphicsScene, 
    QGraphicsSceneDragDropEvent, 
    QGraphicsSceneHoverEvent, 
    QGraphicsSceneMouseEvent, 
    QGraphicsView, 
    QGraphicsItem, 
    QGraphicsRectItem, 
    QGraphicsEllipseItem, 
    QApplication, 
    QPushButton, 
    QGraphicsPathItem,
    QSlider,
    QWidget,
    QVBoxLayout
    )
from PyQt6.QtGui import (
    QBrush, 
    QDragEnterEvent, 
    QMouseEvent, 
    QPen, 
    QColor, 
    QDrag, 
    QPainterPath, 
    QGradient, 
    QRadialGradient, 
    QLinearGradient,
    )
from PyQt6.QtCore import (
    QRectF, 
    Qt, 
    QEvent, 
    QObject, 
    QLineF, 
    QMimeData,
    QPointF
    )

import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../snn" )
import test_network
import math

from qt_node import Node
from qt_edge import Edge


class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.scene = scene

    
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.centerOn(400,300)


        self.visual_time = -1

        # Add Node Button
        button = QPushButton("Add Node")
        button.resize(750, 75)
        button.move(25, 500)
        button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        button.pressed.connect(self.addNodePressed)
        self.addNode = False

        self.scene.addWidget(button)

        self.curId = 0
        self.nodeIds = []
        self.dictOfEdges = {}
        self.edgeBuf = []
    
        self.createTestNetwork()
        self.spike_vec = test_network.test_net_spike_vec()


    # This creates the test network. It will be usurped by code that
    # creates networks from abitrary files/neuro instances
    def createTestNetwork(self):
        n1 = Node(self, 100, 300, 0, "input", self.connectNodes)
        n2 = Node(self, 400, 150, 1, "output", self.connectNodes)
        n3 = Node(self, 400, 300, 2, "output", self.connectNodes)
        n4 = Node(self, 400, 450, 3, "output", self.connectNodes)

        self.scene.addItem(n1); self.scene.addItem(n2);
        self.scene.addItem(n3); self.scene.addItem(n4);
    
        # We have to write some new methods for this
        self.connectNodes(n1, 0); self.connectNodes(n2, 1);
        self.connectNodes(n1, 0); self.connectNodes(n3, 2);
        self.connectNodes(n1, 0); self.connectNodes(n4, 3);
            
        self.dictOfEdges["0->2"].delay = 3

    # When the slider is updated, it updates the visual time for the GUI
    # and then updates all the edges
    def updateSimTimeFromSlider(self, val):
        self.visual_time = val / 10
        print(self.visual_time)

        self.updateEdges()

    # Does whatever mouse click event we want to do
    def mousePressEvent(self, event: QMouseEvent) -> None:
        

        item = self.itemAt(event.pos()) 
        print("You clicked on item", item)


        if self.addNode == True:
                self.addNodeEvent(event)

        return super().mousePressEvent(event)
    
    # Creates a node at user click positon 
    def addNodeEvent(self, event):
        if self.addNode == True:
            widget = Node(self, event.pos().x(), event.pos().y(), self.curId, "input", self.connectNodes)  # Create an instance of MyWidget
            self.curId+=1

            self.scene.addItem(widget)
            self.addNode = False

    # If the buttons pressed, set a flag so the next click creates a node
    def addNodePressed(self):
        print("Add node pressed!")
        self.addNode = True

    # connectNodes is currently passed to the node classes as the function called
    # when the user mouse clicks on them. It maintains a buffer of two nodes
    # such that the first node pressed will connect to the second node.
    def connectNodes(self, obj, id):
        # print(pos1.x(), pos1.y(), id)
        print(f"Clicked on node #{id} at {obj}")
        if len(self.edgeBuf) > 0:
            if id == self.edgeBuf[0][0]:
                return
            self.edgeBuf.append([id, obj])
            linkStr = f"{self.edgeBuf[0][0]}->{id}"
            if linkStr not in self.dictOfEdges:
                print(self.edgeBuf)
                obj1 = self.edgeBuf[0][1]
                
                edge = Edge(obj1, obj) 
                self.dictOfEdges[linkStr] = edge
                self.scene.addItem(edge)

            self.edgeBuf = []
        else:
            self.edgeBuf.append([id, obj])


    # Goes through all edges and tells them to update
    def updateEdges(self):

        for e in self.dictOfEdges:
            
            self.dictOfEdges[e].spike_vec = self.spike_vec[ self.dictOfEdges[e].sourceNode.id ]
            self.dictOfEdges[e].visual_time = self.visual_time


            self.dictOfEdges[e].update()


class Layout(QWidget):

    def __init__(self):
        super().__init__()

        
        vbox = QVBoxLayout(self)
      
        scene = QGraphicsScene(-1500, -1500, 3000, 3000)
        view = AGraphicsView(scene)
        
        # Add Slider for time
        time_slider = QSlider(Qt.Orientation.Horizontal, self)
        time_slider.setRange(0, 100)
        self.visual_time = 0
        time_slider.setValue(0)
        time_slider.move(25, 25)

        time_slider.valueChanged.connect(view.updateSimTimeFromSlider)
        
        vbox.addWidget(time_slider)
        vbox.addWidget(view)

        self.setLayout(vbox)


# Main creates an app with a scence that has a view that is our graphics view.
if __name__ == "__main__":

    app = QApplication(sys.argv)

    layout = Layout()
    layout.show()
    
    app.exec()
