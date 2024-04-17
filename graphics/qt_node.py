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
    QGraphicsPathItem,
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
    QFont,
    QFontMetrics,
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
        super().__init__(0-self.r, 0-self.r, self.d, self.d) 
        self.setPos(x, y)
        self.setZValue(10)
        
        self.nodeType = nodeType
        self.spike_vec = []
        self.input_spikes = []
        self.threshold = 1
        self.title = ""
        self.visual_time = -1
        self.spike_index = 0
        self.spiking = False
        
        self.setToolTip(f"Node ID: {self.id}\nNode Type: {self.nodeType}\nThreshold: {self.threshold}\nTitle: {self.title}\nSpike Vec: {self.spike_vec}")

        self.makeGradient()
        brush = QBrush(self.gradient)
        # self.setFocusP(Qt.FocusPolicy.ClickFocus)
        self.setBrush(brush)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptDrops(True)

        self.titlePathItem = QGraphicsPathItem()
        self.titleBrush = QBrush(QColor(255, 255,255, 255) ) # Black brush
        self.titlePathItem.setBrush(self.titleBrush)
        self.parent.scene.addItem(self.titlePathItem)
        self.titlePathItem.setZValue(100)
        self.titlePath = QPainterPath()
        self.titleFont = QFont("Helvetica", 36)       
        self.draw_title()


        self.titlePathItem.setPath(self.titlePath)
    
    # def setSelected(self, selected: bool) -> None:
    #     self.parent.setSelectedItem(self)
    #     return super().setSelected(selected)

    def draw_title(self):

        fm = QFontMetrics(self.titleFont)
        width = fm.horizontalAdvance(self.title)
        height = fm.height()
        self.titlePath.addText(self.pos().x() - (width / 2), self.pos().y() + (height / 2),  self.titleFont, self.title)

    # If mouse if pressed a second time, it will currently create an edge
    # We should remove that and probably move creating edges to a right click function
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.parent.updateEdges()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent | None) -> None:
        print("Node: is being dragged")
        self.update()
        self.parent.updateEdges(self.id)
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print("Node: Release")
        self.update()
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

        if(self.spiking):
            self.gradient.setColorAt(1, QColor(255, 255, 255, 255))

    def checkSpiking(self, elapsed_spikes):
        for most_recent_spike in elapsed_spikes:
            if most_recent_spike <= self.visual_time and most_recent_spike+0.15 > self.visual_time:  
                self.spiking = True
                return
        self.spiking = False 

    def update(self):
        elapsed_spikes = []
        for spike in self.spike_vec:
            if spike > self.visual_time:
                break
            elapsed_spikes.append(spike)
        
        self.checkSpiking(elapsed_spikes=elapsed_spikes)
        
        self.makeGradient()
        self.setBrush( QBrush(self.gradient) )
        self.setToolTip(f"Node ID: {self.id}\nNode Type: {self.nodeType}\nThreshold: {self.threshold}\nTitle: {self.title}\nSpike Vec: {self.spike_vec}")
        self.titlePath.clear()
        self.draw_title()
        self.titlePathItem.setPath(self.titlePath)

    def outputNodeAsDict(self):

        d = {}

        d["nodeType"] = self.nodeType
        d["title"] = self.title
        d["threshold"] = self.threshold
        d["input_spikes"] = self.input_spikes

        d["posX"] = self.pos().x()
        d["posY"] = self.pos().y()

        return d
