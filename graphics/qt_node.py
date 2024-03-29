"""
This file creates the Node class for the GUI. The Node class extends a QGraphicsEllipseItem
The nodes are added to the GraphicsView and able to be moved and manipulated by the user.
These nodes have data in them corresponding to data from the neuro processor.
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
    QGraphicsTextItem,
    )
from PyQt6.QtGui import (
    QBrush, 
    QDragEnterEvent, 
    QMouseEvent, 
    QPen, 
    QColor, 
    QDrag,
    QPainter,
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
    QPointF
    )



class Node(QGraphicsEllipseItem):
    def __init__(self, parent, x, y, curId, nodeType):
        self.parent = parent

        self.d = 70
        self.r = self.d/2
        self.id = curId
        super().__init__(0-self.r, 0-self.r, self.d, self.d)  # Initialize QPushButton with text "Click Me!"
        self.setPos(x, y)
        self.setZValue(10)
        
        self.nodeType = nodeType
        self.spike_vec = []
        self.input_spikes = []
        self.threshold = 1
        self.title = ""
        
        self.setToolTip(f"Node ID: {self.id}\nNode Type: {self.nodeType}\nThreshold: {self.threshold}\nTitle: {self.title}\nSpike Vec: {self.spike_vec}")

        self.makeGradient()
        brush = QBrush(self.gradient)
        # self.setFocusP(Qt.FocusPolicy.ClickFocus)
        self.setBrush(brush)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptDrops(True)

    # If mouse if pressed a second time, it will currently create an edge
    # We should remove that and probably move creating edges to a right click function
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parent.updateEdges()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("Release")
        self.parent.updateEdges()
        return super().mouseReleaseEvent(event)



    # This function will create the Gradient Brush that will be used to paint the node
    def makeGradient(self):

        # Gradients in QT are kkinda strange, and i'll have to come back and figure exactly where to set the center and focal point
        # for the gradients later. For now, the nodes just end up being a solid color
        self.gradient = QRadialGradient(self.pos().x(), self.pos().y(), self.r, self.pos().x() + self.r /2 , self.pos().y() + self.r /2)


        # Different colors for different types of nodes. Taken from UTK colors
        if(self.nodeType == "input"): # Tennessee orange
            self.gradient.setColorAt(0, QColor(255, 255, 255, 255 ) ) 
            self.gradient.setColorAt(1, QColor(255, 130, 0, 255 ) )
 
        if(self.nodeType == "hidden"): # gray (just gray)
            self.gradient.setColorAt(0, QColor(150, 150, 150, 255 ) ) 
            self.gradient.setColorAt(1, QColor(75, 75, 75, 255 ) )

        if(self.nodeType == "output"): # Pat Summit blue
            self.gradient.setColorAt(0, QColor(255, 255, 255, 255 ) ) 
            self.gradient.setColorAt(1, QColor(72, 159, 233, 255 ) )       

    def update(self):
        self.makeGradient()
        self.setBrush( QBrush(self.gradient) )
        self.setToolTip(f"Node ID: {self.id}\nNode Type: {self.nodeType}\nThreshold: {self.threshold}\nTitle: {self.title}\nSpike Vec: {self.spike_vec}")


    def outputNodeAsDict(self):

        d = {}

        d["nodeType"] = self.nodeType
        d["title"] = self.title
        d["threshold"] = self.threshold
        d["input_spikes"] = self.input_spikes

        d["posX"] = self.pos().x()
        d["posY"] = self.pos().y()

        return d
