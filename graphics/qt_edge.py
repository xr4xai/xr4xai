""" 
This file implements the Edge class for the QT GUI. 
The Edge class extends a QGraphicsPathItem. This is a QT class that uses a path
and implements it plus its functionality onto the graphics view.
The Edge class is created by the parent GraphicsView whenever user action creates
one between two nodes. It is updated whenever the GraphicsView calls updateEdge.
It contains data for its source and sink, as well as weight, delay and spike data
"""


import sys
from typing import Iterable
from PyQt6.QtWidgets import (
    QGraphicsScene, 
    QGraphicsSceneDragDropEvent, 
    QGraphicsSceneHoverEvent, 
    QGraphicsSceneMouseEvent, 
    QGraphicsItem, 
    QGraphicsRectItem, 
    QGraphicsEllipseItem, 
    QGraphicsPathItem,
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
    QPointF
    )

import os
import math


class Edge(QGraphicsPathItem):
    def __init__(self, source, sink, weight = 1, delay = 1):
        self.sourceNode = source
        self.sinkNode = sink
        self.weight = weight
        self.delay = delay

        # This is the data needed to draw spikes along the edges
        # It will be updated by the parent GraphicsView when it calls updateEdges
        # We may want to considerr different ways of updating this.
        self.spike_vec = []
        self.visual_time = -1


        super().__init__()

        self.setToolTip(f"Source ID: {self.sourceNode.id}\nSink ID: {self.sinkNode.id}\nWeight: {self.weight}\nDelay: {self.delay}\nSpike Vec: {self.spike_vec}")

        brush = QBrush(QColor(255, 255, 255, 255) ) # White brush
        self.setBrush(brush)

        self.path = QPainterPath()
       
        self.draw_edge()

        self.setPath(self.path)

    # Update is called whenever the GraphicsView updates the edge
    # All it does is clear the path and then redraw it and readd it
    def update(self):
        self.path.clear()

        self.draw_edge()

        self.setPath(self.path)


    # Draw edge contains the actual code for drawing the edge and its spikes
    # It defintely needs some work yet, particulary in more clearly showing direction
    # and making spikes more clear. PLus they look kinda shitty esp if you the nodes are at a certain angle
    def draw_edge(self):

        # Draws the edge
        self.path.moveTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3 )

        # These bezier curves would look better with differnt end and control points
        self.path.quadTo(self.sinkNode.pos().x() +3, self.sinkNode.pos().y() + 3, self.sinkNode.pos().x() + 3, self.sinkNode.pos().y() + 3 )
        self.path.quadTo(self.sinkNode.pos().x() -  3, self.sinkNode.pos().y() - 3, self.sinkNode.pos().x() - 3, self.sinkNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3, self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3, self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3)
        

        # Draws the spikes currently along the edge onto the edge
        elapsed_spikes = []
        for spike in self.spike_vec:
            if spike > self.visual_time:
                break
            elapsed_spikes.append(spike)

        for most_recent_spike in elapsed_spikes:

            # Determines how far along the spike is
            distance_along_edge = (self.visual_time - most_recent_spike) / self.delay
            print(distance_along_edge)
            if distance_along_edge < 0  or distance_along_edge > 1 :
                continue

            # Offset to circumfrence of the nodes
            offx = (self.sinkNode.pos().x() - self.sourceNode.pos().x() )
            offx /= math.sqrt((self.sinkNode.pos().y() - self.sourceNode.pos().y() ) ** 2 + (self.sinkNode.pos().x() - self.sourceNode.pos().x()) ** 2)
            offx *= self.sourceNode.r
            offy = (self.sinkNode.pos().y() - self.sourceNode.pos().y() )
            offy /= math.sqrt((self.sinkNode.pos().y() - self.sourceNode.pos().y() ) ** 2 + (self.sinkNode.pos().x() - self.sourceNode.pos().x()) ** 2)
            offy *= self.sourceNode.r
            
            # Sets center of spikes such that:
            # Distance_along of 0 puts spike at very end of the visible part of the source side of edge
            # Distance_along of 1 puts spike at very end of the visible part of the sink side of edge
            # Linear mapping for values between there.
            cx = offx + self.sourceNode.pos().x() + distance_along_edge * ( self.sinkNode.pos().x() - self.sourceNode.pos().x() - offx )
            cy = offy + self.sourceNode.pos().y() + distance_along_edge * ( self.sinkNode.pos().y() - self.sourceNode.pos().y() - offy )

            # Debug:
            print(f"{self.sourceNode.id}->{self.sinkNode.id} is drawing a spike at {cx} {cy}. dist_along = {distance_along_edge}")

            # Adds the spike to path
            self.path.addEllipse(QPointF(cx, cy) , 15, 15)

