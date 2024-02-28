import sys
from typing import Iterable
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication, QPushButton
from PyQt6.QtGui import QBrush, QDragEnterEvent, QMouseEvent, QPen, QColor, QDrag
from PyQt6.QtCore import QRectF, Qt, QEvent, QObject, QLineF, QMimeData

app = QApplication(sys.argv)

# Defining a scene rect of 400x200, with it's origin at 0,0.
# If we don't set this on creation, we can set it later with .setSceneRect
class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, curId, edgeFunction):
        self.d = 70
        self.r = self.d/2
        self.id = curId
        super().__init__(0-self.r, 0-self.r, self.d, self.d)  # Initialize QPushButton with text "Click Me!"
        self.setPos(x, y)
        self.setZValue(10)
        self.addEdgeFunc = edgeFunction
        brush = QBrush(QColor("red"))
        # self.setFocusP(Qt.FocusPolicy.ClickFocus)
        self.setBrush(brush)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:

        self.addEdgeFunc(self, self.id)
        return super().mousePressEvent(event)


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
        self.listOfEdges = []
        self.edgeBuf = []

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if self.addNode == True:
                self.addNodeEvent(event)

        return super().mousePressEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent | None) -> None:
        print("Enter")
        
        return super().dragEnterEvent(event)

    def addNodeEvent(self, event):
        if self.addNode == True:
            widget = Node(event.pos().x(), event.pos().y(), self.curId, self.connectNodes)  # Create an instance of MyWidget
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
            if linkStr not in self.listOfEdges:
                print(self.edgeBuf)
                obj1 = self.edgeBuf[0][1]
                self.scene.addLine(QLineF(obj1.pos(), obj.pos()))

                self.listOfEdges.append(linkStr)
            self.edgeBuf = []
        else:
            self.edgeBuf.append([id, obj])
            
        
scene = QGraphicsScene(0, 0, 800, 600)
# scene = AGraphicsScene()

view = AGraphicsView(scene)
view.show()
app.exec()