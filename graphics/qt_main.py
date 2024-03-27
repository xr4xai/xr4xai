"""
This file implements a Layout and Graphics View for the GUI, and the main function that will 
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
    QVBoxLayout,
    QMenu,
    QMenuBar,
    QLineEdit,
    QFormLayout,
    QInputDialog,
    QMainWindow,
    QLayout,
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
    QAction,
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
import network_communication

import math
import json

from qt_node import Node
from qt_edge import Edge


class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.scene = scene

    
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.centerOn(400,300)

        self.createMenuActions()

        self.visual_time = -1

        self.curId = 0
        self.nodeIds = []
        self.dictOfEdges = {}
        self.dictOfNodes = {}
        self.edgeBuf = []
    
        self.createTestNetwork()
        self.spike_vec = test_network.test_net_spike_vec()
        
        self.updateEdges()
        self.updateNodes()


    # This creates the test network. It will be usurped by code that
    # creates networks from abitrary files/neuro instances
    def createTestNetwork(self):
        n1 = Node(self, 100, 300, 0, "input")
        n1.input_spikes = [1, 2, 3]
        n2 = Node(self, 400, 150, 1, "output")
        n3 = Node(self, 400, 300, 2, "output")
        n4 = Node(self, 400, 450, 3, "output")
        self.dictOfNodes[0] = n1; self.dictOfNodes[1] = n2;
        self.dictOfNodes[2] = n3; self.dictOfNodes[3] = n4;
        self.curId = 4

        self.scene.addItem(n1); self.scene.addItem(n2);
        self.scene.addItem(n3); self.scene.addItem(n4);
    
        # We have to write some new methods for this
        self.connectNodes(n1); self.connectNodes(n2);
        self.connectNodes(n1); self.connectNodes(n3);
        self.connectNodes(n1); self.connectNodes(n4);
            
        self.dictOfEdges["0->2"].delay = 3

    # When the slider is updated, it updates the visual time for the GUI
    # and then updates all the edges
    def updateSimTimeFromSlider(self, val):
        self.visual_time = val / 10
        print(self.visual_time)

        self.updateEdges()
        self.updateNodes()


    # Does whatever mouse click event we want to do
    def mousePressEvent(self, event: QMouseEvent) -> None:
        
        # This is a bodge to get event info from any event to be used by other 
        # class member functions without the need to pass the event to them.
        # Probably not the most elegant way to do it, but hey.
        self.mostRecentEvent = event

        item = self.itemAt(event.pos()) 

        if(item is None):

            if(event.button() == Qt.MouseButton.RightButton):
                self.rightClickBackground(event)

        elif(type(item) is Node):

            if(event.button() == Qt.MouseButton.RightButton):
                self.rightClickNode(event)

            elif(event.button() == Qt.MouseButton.LeftButton and len(self.edgeBuf) != 0):
                self.connectNodes(item)


        return super().mousePressEvent(event)

    def rightClickBackground(self, event):

        menu = QMenu(self)

        menu.addAction(self.addNodeAction)

        # Gotta love how to change everything for no reason in new Qt versions
        menu.exec(event.globalPosition().toPoint() )

    def rightClickNode(self, event):

        node = self.itemAt(event.pos() ) 

        menu = QMenu(self)

        menu.addAction(self.addEdgeAction)
        
        nodeTypeMenu = menu.addMenu("Edit Node Type")
        nodeTypeMenu.addAction(self.editNodeTypeInputAction)
        nodeTypeMenu.addAction(self.editNodeTypeHiddenAction)
        nodeTypeMenu.addAction(self.editNodeTypeOutputAction)
        
        if(node.nodeType == "input"):
            menu.addAction(self.editNodeInputSpikesAction) 

        
        menu.exec(event.globalPosition().toPoint() )
        
        

    # Creates a node at user click positon 
    def addNodeEvent(self):
        node = Node(self, self.mostRecentEvent.pos().x(), self.mostRecentEvent.pos().y(), self.curId, "hidden")
        self.dictOfNodes[self.curId] = node
        self.curId+=1

        self.scene.addItem(node)

        self.updateVecs()

    # If the buttons pressed, set a flag so the next click creates a node
    def addNodePressed(self):
        print("Add node pressed!")
        self.addNode = True

    # connectNodes is currently passed to the node classes as the function called
    # when the user mouse clicks on them. It maintains a buffer of two nodes
    # such that the first node pressed will connect to the second node.
    def connectNodes(self, obj): 
       
        if(type(obj) is not Node):
            print("Error in connectNodes: obj is type ", type(obj) )
            return

        id = obj.id

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

        self.updateVecs()

    def updateVecs(self):
        self.spike_vec = network_communication.get_vecs_from_dicts(self.dictOfNodes, self.dictOfEdges)

        self.updateNodes();
        self.updateEdges();

    def updateNodes(self):

        for n in self.dictOfNodes:

            if(n < len(self.spike_vec)):
                self.dictOfNodes[n].spike_vec = self.spike_vec[ n ]
            self.dictOfNodes[n].visual_time = self.visual_time

            self.dictOfNodes[n].update()



    # Goes through all edges and tells them to update
    def updateEdges(self):

        for e in self.dictOfEdges:
            
            if(self.dictOfEdges[e].sourceNode.id < len(self.spike_vec)):
                self.dictOfEdges[e].spike_vec = self.spike_vec[ self.dictOfEdges[e].sourceNode.id ]
            self.dictOfEdges[e].visual_time = self.visual_time


            self.dictOfEdges[e].update()

    # Creates all the actions (and connects them to appropriate functions)
    # for anything and everything that might be used in a menu
    def createMenuActions(self):
        self.addNodeAction = QAction(self)
        self.addNodeAction.setText("Add Node")
        self.addNodeAction.triggered.connect(self.addNodeEvent)
        
        self.addEdgeAction = QAction(self)
        self.addEdgeAction.setText("Create Edge")
        self.addEdgeAction.triggered.connect(lambda: self.connectNodes(self.itemAt(self.mostRecentEvent.pos() )) ) 

        self.editNodeTypeInputAction = QAction(self)
        self.editNodeTypeInputAction.setText("Input")
        self.editNodeTypeInputAction.triggered.connect(lambda: self.editNodeType(self.itemAt(self.mostRecentEvent.pos()), "input" ) )


        self.editNodeTypeHiddenAction = QAction(self)
        self.editNodeTypeHiddenAction.setText("Hidden")
        self.editNodeTypeHiddenAction.triggered.connect(lambda: self.editNodeType(self.itemAt(self.mostRecentEvent.pos()), "hidden" ) ) 
        
        self.editNodeTypeOutputAction = QAction(self)
        self.editNodeTypeOutputAction.setText("Output")
        self.editNodeTypeOutputAction.triggered.connect(lambda: self.editNodeType(self.itemAt(self.mostRecentEvent.pos()), "output" ) ) 
    
        self.editNodeInputSpikesAction = QAction(self)
        self.editNodeInputSpikesAction.setText("Edit Input Spikes")
        self.editNodeInputSpikesAction.triggered.connect(lambda: self.editInputSpikes(self.itemAt(self.mostRecentEvent.pos()) ) ) 
    
    def saveNetworkToFile(self):

        fn, ok = QInputDialog.getText(self, "Save As", "Save Network to File: ", QLineEdit.EchoMode.Normal, "" )
        
        if ok and fn:
            network_communication.write_to_file(self.dictOfNodes, self.dictOfEdges, fn)


    def openNetworkFile(self):

        
        fn, ok = QInputDialog.getText(self, "Open", "File to Open:  ", QLineEdit.EchoMode.Normal, "" )
        
        if ok and fn:
            self.scene.clear()

            self.dictOfNodes, self.dictOfEdges = network_communication.read_from_file(fn, self)
            
            for n in self.dictOfNodes.values():
                self.scene.addItem(n)
            for e in self.dictOfEdges.values():
                self.scene.addItem(e)

            self.updateVecs()

    def editNodeType(self, node, newtype):

        node.nodeType = newtype

        self.reorderNodeIds()
        self.updateVecs()

    def editInputSpikes(self, node):

        input_string = "["
        for i in node.input_spikes:
            input_string += " " + str(i) + " , "

        input_string += "]"

        text, ok = QInputDialog.getText(self, "Input Spike Editor", "Edit Input Spikes:", QLineEdit.EchoMode.Normal, input_string )
        
        if ok and text:
            input_spikes = []
            for x in text.split(',') :
                try:
                    input_spikes.append( int(x.lstrip('[').rstrip(']').strip()) )
                except ValueError:
                    print(x + " in input not castable to int.")

            node.input_spikes = input_spikes

            self.updateVecs()
        
    """
    Okay, so the neuroprocessor demands that input node ids come before output/hidden node ids.
    I don't particullary like this, but what do I know.
    In any case, we have to make sure the node IDs are in the correct order, so this function does that any time a node type is changed 
    """
    def reorderNodeIds(self):
        
        input_nodes = []
        hidden_nodes = []
        output_nodes = []
        
        newNodeDict = {}
        newEdgeDict = {}
            
        # This is a dict of the new ids keyed on the old ones
        oldToNewDict = {}

        for n in self.dictOfNodes.values():
            if(n.nodeType == "input"):
                input_nodes.append(n)
            elif(n.nodeType == "hidden"):
                hidden_nodes.append(n)
            else:
                output_nodes.append(n)

        for i in range(len(input_nodes)):
            oldToNewDict[input_nodes[i].id] = i
            input_nodes[i].id = i
            newNodeDict[i] = input_nodes[i]
    
        for i in range(len(hidden_nodes)):
            oldToNewDict[hidden_nodes[i].id] = i + len(input_nodes)
            hidden_nodes[i].id = i + len(input_nodes)
            newNodeDict[i + len(input_nodes) ] = hidden_nodes[i]

        for i in range(len(output_nodes)):
            oldToNewDict[output_nodes[i].id] = i + len(input_nodes) + len(hidden_nodes)
            output_nodes[i].id = i + len(input_nodes) + len(hidden_nodes)
            newNodeDict[i + len(hidden_nodes) + len(input_nodes) ] = output_nodes[i]

        for e in self.dictOfEdges.values():
            key = str(e.sourceNode) + "->" + str(e.sinkNode)

            newEdgeDict[key] = e

        self.dictOfEdges = newEdgeDict
        self.dictOfNodes = newNodeDict





class Layout(QWidget):

    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout(self)
      
        self.scene = QGraphicsScene(-1500, -1500, 3000, 3000)
        self.view = AGraphicsView(self.scene)
        
        # Add Slider for time
        time_slider = QSlider(Qt.Orientation.Horizontal, self)
        time_slider.setRange(0, 100)
        self.visual_time = 0
        time_slider.setValue(0)
        time_slider.move(25, 25)

        time_slider.valueChanged.connect(self.view.updateSimTimeFromSlider)

        vbox.addWidget(time_slider)
        vbox.addWidget(self.view)

        menuBar = QMenuBar(self)    
        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        self.saveAction = QAction("Save As", self.view)
        self.saveAction.triggered.connect(self.view.saveNetworkToFile)
        
        self.openAction = QAction("Open", self.view)
        self.openAction.triggered.connect(self.view.openNetworkFile)

        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.openAction)

        vbox.setMenuBar(menuBar)
    
        self.setLayout(vbox)
   
# Main creates an app with a scence that has a view that is our graphics view.
if __name__ == "__main__":

    app = QApplication(sys.argv)

    layout = Layout()
    layout.show()

    app.exec()
