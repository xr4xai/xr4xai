import sys
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication, QPushButton
from PyQt6.QtGui import QBrush, QMouseEvent, QPen, QColor
from PyQt6.QtCore import Qt, QEvent, QObject

app = QApplication(sys.argv)

# Defining a scene rect of 400x200, with it's origin at 0,0.
# If we don't set this on creation, we can set it later with .setSceneRect
class MyWidget(QGraphicsEllipseItem):
    def __init__(self, x, y, edgeFunction):
        self.d = 70
        self.r = self.d/2
        super().__init__(x-self.r, y-self.r, self.d, self.d)  # Initialize QPushButton with text "Click Me!"
        self.setZValue(10)
        self.addEdgeFunc = edgeFunction
        brush = QBrush(QColor("red"))
        # self.setFocusP(Qt.FocusPolicy.ClickFocus)
        self.setBrush(brush)

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.addEdgeFunc(event.pos(), self.pos())


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
            widget = MyWidget(event.pos().x(), event.pos().y(), self.connectNodes)  # Create an instance of MyWidget

            self.scene.addItem(widget)
            self.addNode = False

    def addNodePressed(self):
        print("Pressed!")
        self.addNode = True

    # def PressEvent(self, event: QGraphicsSceneMouseEvent):
    #     print("Button clicked!", self, event)  # Connect button click signal to a function

    def connectNodes(self, pos1, pos2):
        print(pos1, pos2)
        
scene = QGraphicsScene(0, 0, 800, 600)
# scene = AGraphicsScene()

view = AGraphicsView(scene)
view.show()
app.exec()