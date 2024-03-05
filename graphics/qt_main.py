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

# Global value visual_time repesents the time in the simulations currently shown
# It will get updated by the GraphicsView
visual_time = -1


class Node(QGraphicsEllipseItem):
    def __init__(self, parent, x, y, curId, nodeType, edgeFunction):
        self.parent = parent

        self.d = 70
        self.r = self.d/2
        self.id = curId
        super().__init__(0-self.r, 0-self.r, self.d, self.d)  # Initialize QPushButton with text "Click Me!"
        self.setPos(x, y)
        self.setZValue(10)
        
        self.nodeType = nodeType

        self.addEdgeFunc = edgeFunction
            

        self.makeGradient()
        brush = QBrush(self.gradient)
        # self.setFocusP(Qt.FocusPolicy.ClickFocus)
        self.setBrush(brush)
        self._new = True

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if not self._new:
            self.addEdgeFunc(self, self.id)
        else:
            self._new = False
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("Release")
        self.parent.updateEdges()
        return super().mouseReleaseEvent(event)

    def makeGradient(self):
        self.gradient = QRadialGradient(self.pos().x(), self.pos().y(), self.r, self.pos().x() + self.r /2 , self.pos().y() + self.r /2)

        #self.gradient.setSpread(QGradient.Spread.ReflectSpread)

        if(self.nodeType == "input"): # Tennessee orange
            self.gradient.setColorAt(0, QColor(255, 255, 255, 255 ) ) 
            self.gradient.setColorAt(1, QColor(255, 130, 0, 255 ) )
 
        if(self.nodeType == "hidden"): # gray
            self.gradient.setColorAt(0, QColor(150, 150, 150, 255 ) ) 
            self.gradient.setColorAt(1, QColor(75, 75, 75, 255 ) )
            
        if(self.nodeType == "output"): # Pat Summit blue
            self.gradient.setColorAt(0, QColor(255, 255, 255, 255 ) ) 
            self.gradient.setColorAt(1, QColor(72, 159, 233, 255 ) )       


class Edge(QGraphicsPathItem):
    def __init__(self, source, sink, weight = 1, delay = 1):
        self.sourceNode = source
        self.sinkNode = sink
        self.weight = weight
        self.delay = delay

        self.spike_vec = []

        super().__init__()

        brush = QBrush(QColor(255, 255, 255, 255) ) # White brush
        self.setBrush(brush)

        self.path = QPainterPath()
       
        self.draw_edge()

        self.setPath(self.path)


    def update(self):
        self.path.clear()

        self.draw_edge()

        self.setPath(self.path)

    def draw_edge(self):

        self.path.moveTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3 )

        self.path.quadTo(self.sinkNode.pos().x() +3, self.sinkNode.pos().y() + 3, self.sinkNode.pos().x() + 3, self.sinkNode.pos().y() + 3 )
        self.path.quadTo(self.sinkNode.pos().x() -  3, self.sinkNode.pos().y() - 3, self.sinkNode.pos().x() - 3, self.sinkNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3, self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3, self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3)
        
        elapsed_spikes = []
        for spike in self.spike_vec:
            if spike > visual_time:
                break
            elapsed_spikes.append(spike)

        for most_recent_spike in elapsed_spikes:

            distance_along_edge = (visual_time - most_recent_spike) / self.delay
            print(distance_along_edge)
            if distance_along_edge < 0  or distance_along_edge > 1 :
                continue

            offx = (self.sinkNode.pos().x() - self.sourceNode.pos().x() ) 
            offx /= math.sqrt((self.sinkNode.pos().y() - self.sourceNode.pos().y() ) ** 2 + (self.sinkNode.pos().x() - self.sourceNode.pos().x()) ** 2) 
            offx *= self.sourceNode.r
            offy = (self.sinkNode.pos().y() - self.sourceNode.pos().y() )
            offy /= math.sqrt((self.sinkNode.pos().y() - self.sourceNode.pos().y() ) ** 2 + (self.sinkNode.pos().x() - self.sourceNode.pos().x()) ** 2)
            offy *= self.sourceNode.r
            cx = offx + self.sourceNode.pos().x() + distance_along_edge * ( self.sinkNode.pos().x() - self.sourceNode.pos().x() )
            cy = offy + self.sourceNode.pos().y() + distance_along_edge * ( self.sinkNode.pos().y() - self.sourceNode.pos().y() )

            print(f"{self.sourceNode.id}->{self.sinkNode.id} is drawing a spike at {cx} {cy}. dist_along = {distance_along_edge}")

            self.path.addEllipse(QPointF(cx, cy) , 15, 15)




class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.scene = scene
        
        # Add Node Button
        button = QPushButton("Add Node")
        button.resize(750, 75)
        button.move(25, 500)
        button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        button.pressed.connect(self.addNodePressed)
        self.addNode = False

        self.scene.addWidget(button)

        # Add Slider for time
        time_slider = QSlider(Qt.Orientation.Horizontal, self)
        time_slider.setRange(0, 100)
        visual_time = 0
        time_slider.setValue(0)
        time_slider.move(25, 25)

        time_slider.valueChanged.connect(self.updateSimTimeFromSlider)
        
        self.scene.addWidget(time_slider)

        self.curId = 0
        self.nodeIds = []
        self.dictOfEdges = {}
        self.edgeBuf = []
    
        self.createTestNetwork()
        self.spike_vec = test_network.test_net_spike_vec()


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

    def updateSimTimeFromSlider(self, val):
        global visual_time
        visual_time = val / 10
        print(visual_time)

        self.updateEdges()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.addNode == True:
                self.addNodeEvent(event)

        return super().mousePressEvent(event)
    
    def addNodeEvent(self, event):
        if self.addNode == True:
            widget = Node(self, event.pos().x(), event.pos().y(), self.curId, "input", self.connectNodes)  # Create an instance of MyWidget
            self.curId+=1

            self.scene.addItem(widget)
            self.addNode = False

    def addNodePressed(self):
        print("Add node pressed!")
        self.addNode = True

    # def PressEvent(self, event: QGraphicsSceneMouseEvent):
    #     print("Button clicked!", self, event)  # Connect button click signal to a function

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

    def updateEdges(self):

        for e in self.dictOfEdges:
            #self.scene.removeItem(self.dictOfEdgeItems[e])
            
            
            self.dictOfEdges[e].spike_vec = self.spike_vec[ self.dictOfEdges[e].sourceNode.id ]

            self.dictOfEdges[e].update()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    scene = QGraphicsScene(0, 0, 800, 600)
    # scene = AGraphicsScene()

    view = AGraphicsView(scene)
    view.show()
    app.exec()
