import sys
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication, QPushButton
from PyQt6.QtGui import QBrush, QMouseEvent, QPen, QColor
from PyQt6.QtCore import Qt, QEvent, QObject, QLineF

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

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.addEdgeFunc(self.pos(), self.id)


class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.scene = scene
        self.installEventFilter(self)

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

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a1.type() == QEvent.Type.MouseButtonPress:
            if self.addNode == True:
                self.addNodeEvent(a1)
                return True
            else:
                return False
        return False


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

    def connectNodes(self, pos, id):
        # print(pos1.x(), pos1.y(), id)
        print(f"Clicked on node #{id} at {pos}")
        if len(self.edgeBuf) > 0:
            self.edgeBuf.append([id, pos])
            linkStr = f"{self.edgeBuf[0][0]}->{id}"
            if linkStr not in self.listOfEdges:
                print(self.edgeBuf)
                pos1 = self.edgeBuf[0][1]
                self.scene.addLine(QLineF(pos1, pos))

                self.listOfEdges.append(linkStr)
            self.edgeBuf = []
        else:
            self.edgeBuf.append([id, pos])
            
        
scene = QGraphicsScene(0, 0, 800, 600)
# scene = AGraphicsScene()

view = AGraphicsView(scene)
view.show()
app.exec()