import sys
from typing import Iterable
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication, QPushButton, QGraphicsPathItem
from PyQt6.QtGui import QBrush, QDragEnterEvent, QMouseEvent, QPen, QColor, QDrag, QPainterPath, QGradient, QRadialGradient, QLinearGradient
from PyQt6.QtCore import QRectF, Qt, QEvent, QObject, QLineF, QMimeData


# Defining a scene rect of 400x200, with it's origin at 0,0.
# If we don't set this on creation, we can set it later with .setSceneRect
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
    def __init__(self, source, sink):
        self.sourceNode = source
        self.sinkNode = sink

        super().__init__()

        brush = QBrush(QColor(255, 255, 255, 255) ) # White brush
        self.setBrush(brush)

        self.path = QPainterPath()
       
        self.draw_edge()

        self.setPath(self.path)


    def update(self):
        print(self)

        self.path.clear()

        self.draw_edge()

        self.setPath(self.path)

    def draw_edge(self):

        self.path.moveTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3 )

        self.path.quadTo(self.sinkNode.pos().x() +3, self.sinkNode.pos().y() + 3, self.sinkNode.pos().x() + 3, self.sinkNode.pos().y() + 3 )
        self.path.quadTo(self.sinkNode.pos().x() -  3, self.sinkNode.pos().y() - 3, self.sinkNode.pos().x() - 3, self.sinkNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3, self.sourceNode.pos().x() - 3, self.sourceNode.pos().y() - 3 )
        self.path.quadTo(self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3, self.sourceNode.pos().x() + 3, self.sourceNode.pos().y() + 3)



class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.scene = scene

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
        self.dictOfEdgeItems = {}
        self.edgeBuf = []

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
            self.dictOfEdges[e].update()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    scene = QGraphicsScene(0, 0, 800, 600)
    # scene = AGraphicsScene()

    view = AGraphicsView(scene)
    view.show()
    app.exec()
