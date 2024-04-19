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
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QLineEdit,
    QFormLayout,
    QInputDialog,
    QMainWindow,
    QLayout,
    QLabel,
    QTableWidget,
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
    QPointF,
    QTimer,
    )

import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../snn" )
# import test_network
import network_communication

import math
import json

from qt_node import Node
from qt_edge import Edge


class AGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, layout: QLayout):
        super().__init__(scene)
        self.scene: QGraphicsScene = scene
        self.layout: QLayout = layout
    
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.centerOn(400,300)

        self.selectedItem = None

        self.ribbon: QHBoxLayout = QHBoxLayout()
        self.none_ribbon_list = self.createNoneRibbon()
        self.node_ribbon_list = self.createNodeRibbon()
        self.edge_ribbon_list = self.createEdgeRibbon()

        self.changeRibbon(None)
        self.createMenuActions()

        # self.none_ribbon = self.getNoneRibbon()

        self.visual_time = 0
        self.minimum_time = 0
        self.maximum_time = 10

        self.curId = 0
        self.nodeIds = []
        self.dictOfEdges = {}
        self.dictOfNodes = {}
        self.edgeBuf = []

        self.scene.selectionChanged.connect(self.selectionChanged)
    
        self.createTestNetwork()
        self.updateVecs() 

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
        self.visual_time = val / self.layout.tps        
        self.layout.timelabel.setText( rf't = {self.visual_time:.2f}')
        #print(self.visual_time)

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
            # This is very much a temparary solution
            self.scene.clearSelection()
            item.setSelected(True)

            if(event.button() == Qt.MouseButton.RightButton):
                self.rightClickNode(event)

            elif(event.button() == Qt.MouseButton.LeftButton and len(self.edgeBuf) != 0):
                self.connectNodes(item)
        
        elif(type(item) is Edge):
            # This is very much a temparary solution
            self.scene.clearSelection()
            item.setSelected(True)

            if(event.button() == Qt.MouseButton.RightButton):
                self.rightClickEdge(event)

        return super().mousePressEvent(event)


    # This is called anytime that the slection is changed
    def selectionChanged(self):
        selectedItems = self.scene.selectedItems()
        if len(selectedItems) > 0:
            self.selectedItem = selectedItems[0]
            if (type(self.selectedItem) == Node):
                print(f"Main: Node {self.selectedItem.id} selected")
    
    # Creating the ribbon for when nothing is selected
    def createNoneRibbon(self):
        list_of_widgets = []
        self.add_input_button = QPushButton("Add &Input Node",self)
        self.add_hidden_button = QPushButton("Add &Hidden Node",self)
        self.add_output_button = QPushButton("Add &Output Node",self)

        list_of_widgets.append(self.add_input_button)
        list_of_widgets.append(self.add_hidden_button)
        list_of_widgets.append(self.add_output_button)

        self.add_input_button.clicked.connect(lambda: self.addNodeEvent("input", QPointF(0, 0)))
        self.add_hidden_button.clicked.connect(lambda: self.addNodeEvent("hidden", QPointF(0, 0)))
        self.add_output_button.clicked.connect(lambda: self.addNodeEvent("output", QPointF(0, 0)))

        self.ribbon.addWidget(self.add_input_button)
        self.ribbon.addWidget(self.add_hidden_button)
        self.ribbon.addWidget(self.add_output_button)

        return list_of_widgets

    def createNodeRibbon(self):
        node_ribbon = []

        self.threshold_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold_slider.setRange(-10, 10)
        self.threshold_slider.setValue(0)
        self.threshold_slider.move(25, 25)

        self.n_delete_button = QPushButton("&Delete",self)
        self.n_delete_button.clicked.connect(self.handleNDelete)

        node_ribbon.append(self.threshold_slider) 
        node_ribbon.append(self.n_delete_button)

        for widget in node_ribbon:
            self.ribbon.addWidget(widget)

        return node_ribbon

    def createEdgeRibbon(self):
        edge_ribbon = []

        self.weightLabel = QLabel(self)
        self.weightLabel.setText("Weight")

        self.e_weight_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.e_weight_slider.setRange(-10, 10)
        self.e_weight_slider.setValue(0)
        self.e_weight_slider.move(25, 25)
        self.threshold_slider.setTickInterval(1)
        self.e_weight_slider.valueChanged.connect(self.handleEWeightSlider)

        self.e_weight_text = QLineEdit(self, text="")
        self.e_weight_text.textChanged.connect(self.handleEWeightText)
        self.e_weight_text.setMaximumWidth(50)        
        self.e_weight_text.setToolTip("Edge's Weight")

        self.delayLabel = QLabel(self)
        self.delayLabel.setText("Delay")

        self.e_delay_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.e_delay_slider.setRange(10, 50)
        self.e_delay_slider.setValue(0)
        self.e_delay_slider.move(25, 25)
        self.threshold_slider.setTickInterval(1)
        self.e_delay_slider.valueChanged.connect(self.handleEDelaySlider)

        self.e_delay_text = QLineEdit(self, text="")
        self.e_delay_text.textChanged.connect(self.handleEDelayText)
        self.e_delay_text.setMaximumWidth(50)        
        self.e_delay_text.setToolTip("Edge's Delay")

        self.e_delete_button = QPushButton("&Delete",self)
        self.e_delete_button.clicked.connect(self.handleEDelete)

        edge_ribbon.append(self.weightLabel)
        edge_ribbon.append(self.e_weight_slider)
        edge_ribbon.append(self.e_weight_text)
        edge_ribbon.append(self.delayLabel)
        edge_ribbon.append(self.e_delay_slider)
        edge_ribbon.append(self.e_delay_text)
        edge_ribbon.append(self.e_delete_button)

        for widget in edge_ribbon:
            self.ribbon.addWidget(widget)

        return edge_ribbon

    def updateRibbon(self):
        if type(self.selectedItem) == Node:
            self.threshold_slider.setValue(int(self.selectedItem.threshold * 10))
        if type(self.selectedItem) == Edge:
            self.e_weight_slider.setValue(int(self.selectedItem.weight * 10))
            self.e_weight_text.setText(str(self.selectedItem.weight))
            self.e_delay_slider.setValue(int(self.selectedItem.delay * 10))
            self.e_delay_text.setText(str(self.selectedItem.delay))

    def hideAll(self):
        for list in [self.edge_ribbon_list, self.node_ribbon_list, self.none_ribbon_list]:
            if len(list) > 0:
                for widget in list:
                    widget.hide()
    
    def unhideList(self, list):
        if len(list) > 0:
            for widget in list:
                widget.show()

    def changeRibbon(self, sel_type): 
        self.hideAll()

        if (sel_type == Node):
            self.unhideList(self.node_ribbon_list)
        elif (sel_type == Edge):
            self.unhideList(self.edge_ribbon_list)
        else:
            self.unhideList(self.none_ribbon_list)

        self.updateRibbon()

    def getRibbon(self) -> QHBoxLayout:
        return self.ribbon

    def rightClickBackground(self, event):

        menu = QMenu(self)

        # menu.addAction(self.addNodeAction)
        nodeTypeMenu = menu.addMenu("Add Node")
        nodeTypeMenu.addAction(self.addNodeActionInput)
        nodeTypeMenu.addAction(self.addNodeActionHidden)
        nodeTypeMenu.addAction(self.addNodeActionOutput)

        # Gotta love how to change everything for no reason in new Qt versions
        menu.exec(event.globalPosition().toPoint() )

    def rightClickNode(self, event):

        node = self.itemAt(event.pos() ) 

        menu = QMenu(self)

        menu.addAction(self.addEdgeAction)
        menu.addAction(self.editNodeTitleAction)
        menu.addAction(self.editNodeThresholdAction)

        nodeTypeMenu = menu.addMenu("Edit Node Type")
        nodeTypeMenu.addAction(self.editNodeTypeInputAction)
        nodeTypeMenu.addAction(self.editNodeTypeHiddenAction)
        nodeTypeMenu.addAction(self.editNodeTypeOutputAction)
        
        menu.addAction(self.deleteNodeAction)


        if(node.nodeType == "input"):
            menu.addAction(self.editNodeInputSpikesAction) 

        
        menu.exec(event.globalPosition().toPoint() )

    def rightClickEdge(self, event):

        edge = self.itemAt(event.pos() )

        menu = QMenu(self)

        menu.addAction(self.editEdgeWeightAction)
        menu.addAction(self.editEdgeDelayAction)
        menu.addAction(self.deleteEdgeAction)

        menu.exec(event.globalPosition().toPoint() )
        

    # Creates a node at user click positon 
    def addNodeEvent(self, type, pos=None):
        if (pos == None):
            pos = self.mostRecentEvent.pos()

        node = Node(self, pos.x(), pos.y(), self.curId, type)
        self.dictOfNodes[self.curId] = node
        self.curId+=1

        self.scene.addItem(node)
        
        self.reorderNodeIds()
        self.updateVecs()

    # If the buttons pressed, set a flag so the next click creates a node
    def addNodePressed(self):
        print("Main: Add node pressed!")
        self.addNode = True

    # connectNodes is currently passed to the node classes as the function called
    # when the user mouse clicks on them. It maintains a buffer of two nodes
    # such that the first node pressed will connect to the second node.
    def connectNodes(self, obj): 
       
        if(type(obj) is not Node):
            print("Main: Error in connectNodes: obj is type ", type(obj) )
            return

        id = obj.id

        if len(self.edgeBuf) > 0:
            if id == self.edgeBuf[0][0]:
                return
            self.edgeBuf.append([id, obj])
            linkStr = f"{self.edgeBuf[0][0]}->{id}"
            if linkStr not in self.dictOfEdges:
                print(f"Main: self.edgeBuf")
                obj1 = self.edgeBuf[0][1]
                
                edge = Edge(obj1, obj) 
                self.dictOfEdges[linkStr] = edge
                self.scene.addItem(edge)

            self.edgeBuf = []
        else:
            self.edgeBuf.append([id, obj])

        self.updateVecs()

    def updateVecs(self):
        self.spike_vec = network_communication.get_vecs_from_dicts(self.dictOfNodes, self.dictOfEdges, min = self.minimum_time, max = self.maximum_time)

        self.updateNodes();
        self.updateEdges();

    def updateNodes(self):

        for n in self.dictOfNodes:

            if(n < len(self.spike_vec)):
                self.dictOfNodes[n].spike_vec = self.spike_vec[ n ]
            self.dictOfNodes[n].visual_time = self.visual_time

            self.dictOfNodes[n].update()



    # Goes through all edges and tells them to update
    def updateEdges(self, nodeID=-999):

        for e in self.dictOfEdges:
            
            if(self.dictOfEdges[e].sourceNode.id < len(self.spike_vec)):
                self.dictOfEdges[e].spike_vec = self.spike_vec[ self.dictOfEdges[e].sourceNode.id ]
            self.dictOfEdges[e].visual_time = self.visual_time

            if (nodeID == -999):
                print("Main: Update All")
                self.dictOfEdges[e].update()
            elif (self.dictOfEdges[e].sourceNode.id == nodeID or self.dictOfEdges[e].sinkNode.id == nodeID):
                print("Main: Update one")
                self.dictOfEdges[e].update()

    # Creates all the actions (and connects them to appropriate functions)
    # for anything and everything that might be used in a menu
    def createMenuActions(self):
        self.addNodeActionHidden = QAction(self, text="Hidden")
        self.addNodeActionHidden.triggered.connect(lambda: self.addNodeEvent("hidden"))
        
        self.addNodeActionInput = QAction(self, text="Input")
        self.addNodeActionInput.triggered.connect(lambda: self.addNodeEvent("input"))

        self.addNodeActionOutput = QAction(self, text="Output")
        self.addNodeActionOutput.triggered.connect(lambda: self.addNodeEvent("output"))

        self.addEdgeAction = QAction(self, text="Create Edge")
        self.addEdgeAction.triggered.connect(lambda: self.connectNodes(self.itemAt(self.mostRecentEvent.pos() )) ) 

        self.editNodeTitleAction = QAction(self, text="Edit Node Title")
        self.editNodeTitleAction.triggered.connect(lambda: self.editNodeTitle(self.itemAt(self.mostRecentEvent.pos() ) ) )

        self.editNodeThresholdAction = QAction(self)
        self.editNodeThresholdAction.setText("Edit Node Threshold")
        self.editNodeThresholdAction.triggered.connect(lambda: self.editNodeThreshold(self.itemAt(self.mostRecentEvent.pos() ) ) )

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
    
        self.editEdgeWeightAction = QAction(self)
        self.editEdgeWeightAction.setText("Edit Edge Weight")
        self.editEdgeWeightAction.triggered.connect(lambda: self.editEdgeWeight(self.itemAt(self.mostRecentEvent.pos() ) ) )

        self.editEdgeDelayAction = QAction(self)
        self.editEdgeDelayAction.setText("Edit Edge Delay")
        self.editEdgeDelayAction.triggered.connect(lambda: self.editEdgeDelay(self.itemAt(self.mostRecentEvent.pos() ) ) )

        self.deleteEdgeAction = QAction(self)
        self.deleteEdgeAction.setText("Delete Edge")
        self.deleteEdgeAction.triggered.connect(lambda: self.deleteEdge(self.itemAt(self.mostRecentEvent.pos() ) ) )

        self.deleteNodeAction = QAction(self)
        self.deleteNodeAction.setText("Delete Node")
        self.deleteNodeAction.triggered.connect(lambda: self.deleteNode(self.itemAt(self.mostRecentEvent.pos() ) ) )
    
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

    def editNodeTitle(self, node):
        
        text, ok = QInputDialog.getText(self, "Edit Title", "Change Node Title", QLineEdit.EchoMode.Normal, node.title )

        if ok and text:
            node.title = text
            self.updateNodes()     

    def editNodeThreshold(self, node):
        
        text, ok = QInputDialog.getText(self, "Edit Threshold", "Change Node Threshold", QLineEdit.EchoMode.Normal, str(node.threshold) )

        if ok and text:
            try:
                node.threshold = float(text)
                
            except ValueError:
                    print(text, " is not castable to float")

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

    def handleEWeightSlider(self, Weight):
        self.selectedItem.weight = float(Weight)/10
        self.updateVecs()
        self.updateRibbon()

    def handleEWeightText(self, Weight):
        self.selectedItem.weight = float(Weight)
        self.updateVecs()
        self.updateRibbon()
        
    def editEdgeWeight(self, edge):
        
        text, ok = QInputDialog.getText(self, "Edit Edge Weight", "Change Edge Weight", QLineEdit.EchoMode.Normal, str(edge.weight) )

        if ok and text:
            try:
                edge.weight = float(text)
                
            except ValueError:
                    print(text, " is not castable to float")

            self.updateVecs()
        self.updateRibbon()

    def handleEDelaySlider(self, delay):
        self.selectedItem.delay = float(delay)/10
        self.updateVecs()
        self.updateRibbon()

    def handleEDelayText(self, delay):
        self.selectedItem.delay = float(delay)
        self.updateVecs()
        self.updateRibbon()
    
    def editEdgeDelay(self, edge):
        
        text, ok = QInputDialog.getText(self, "Edit Delay", "Change Edge Delay", QLineEdit.EchoMode.Normal, str(edge.delay) )

        if ok and text:
            try:
                edge.delay = float(text)
                
            except ValueError:
                    print(text, " is not castable to float")

            self.updateVecs()
        self.updateRibbon()
    
    def handleEDelete(self):
        self.deleteEdge(self.selectedItem)

    def deleteEdge(self, edge):
        key = str(edge.sourceNode.id) + "->" + str(edge.sinkNode.id)
        
        try:
            self.dictOfEdges.pop(key)
            self.scene.removeItem(edge)
        except KeyError:
            print("The key ", key, " is not in the dict somehow. Uhhhhhh. Idk how we could even get to this state.")

        self.updateVecs()
        self.updateRibbon()

    def handleNDelete(self):
        self.deleteNode(self.selectedItem)
    
    def deleteNode(self, node):
        key = node.id

        try:
            to_del = []            
            for e in self.dictOfEdges:
                if self.dictOfEdges[e].sourceNode.id == key or self.dictOfEdges[e].sinkNode.id == key:
                    to_del.append(self.dictOfEdges[e])        
            for e in to_del:
                self.deleteEdge(e)

            self.dictOfNodes.pop(key)
            self.scene.removeItem(node)
            
            self.reorderNodeIds()

        except KeyError:
            print("The key is not in the dict somehow. Uhhhhhh. Idk how we could even get to this state.")

        self.updateVecs()
        self.updateRibbon()


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
            key = str(e.sourceNode.id) + "->" + str(e.sinkNode.id)

            newEdgeDict[key] = e

        self.dictOfEdges = newEdgeDict
        self.dictOfNodes = newNodeDict
        self.curId = len(newNodeDict)


    


class Layout(QWidget):

    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout(self)
        self.ribbon = QVBoxLayout(self)
      
        self.scene = QGraphicsScene(-1500, -1500, 3000, 3000)
        self.view = AGraphicsView(self.scene, self)
        
        self.timebox = QHBoxLayout(self)

        self.play_button = QPushButton("&Play",self)
        self.is_playing = False
        self.play_button.clicked.connect(self.playButtonClicked)
        

        self.minText = QLineEdit(self)
        self.minText.setText('0')
        self.minText.textChanged.connect(self.minTextChanged)
        self.minText.setMaximumWidth( 50 ) 
        self.minText.setToolTip("Minimum Time")

        # Add Slider for time
        self.time_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.time_slider.setRange(0, 2000)
        self.visual_time = 0
        self.time_slider.setValue(0)
        self.time_slider.move(25, 25)

        self.time_slider.valueChanged.connect(self.view.updateSimTimeFromSlider)

        # Label for time
        self.timelabel = QLabel()
        self.timelabel.setText( rf't = {self.view.visual_time:.2f}')
        self.timelabel.setToolTip("Current Simulation Time")

        # max time box
        self.maxText = QLineEdit(self)
        self.maxText.setText('10')
        self.maxText.textChanged.connect(self.maxTextChanged)
        self.maxText.setMaximumWidth( 50)        
        self.maxText.setToolTip("Maximum Time")

        self.timebox.addWidget(self.play_button)
        self.timebox.addWidget(self.minText)
        self.timebox.addWidget(self.time_slider)
        self.timebox.addWidget(self.timelabel)
        self.timebox.addWidget(self.maxText)


        # Ribbon Implimentation {
        self.view.scene.selectionChanged.connect(self.changedFocus)
        self.selectedItem = None

        self.curr_ribbon = self.view.getRibbon()

        # self.edge_ribbon.addWidget(self.weight_slider)

        self.ribbon.addLayout(self.timebox)
        self.ribbon.addLayout(self.curr_ribbon)
        # }

        vbox.addLayout(self.ribbon)
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

        self.tps = 20
        self.fps = 20
        self.timer = QTimer()
        self.timer.setInterval(int(1000 / self.fps))
        self.timer.timeout.connect(self.update)
        self.time_slider.setRange(self.view.minimum_time * self.tps, self.tps * self.view.maximum_time)
        

    def changedFocus(self):
        selectedItems = self.view.scene.selectedItems()
        if len(selectedItems) > 0:
            self.selectedItem = selectedItems[0]
            self.view.changeRibbon(type(self.selectedItem))
        elif(len(selectedItems) == 0):
            self.view.changeRibbon(None)

    def playButtonClicked(self):
        if(self.is_playing):
            self.play_button.setText("&Play")
            self.is_playing = False
            self.timer.stop()
        else:
            if(self.time_slider.value() >= self.tps * self.view.maximum_time ):
                self.time_slider.setValue(self.view.minimum_time * self.tps)

            self.play_button.setText("Pause")
            self.is_playing = True
            self.timer.start()

    def minTextChanged(self):
        try:
            new_min = float(self.minText.text() )
            if(new_min < self.view.maximum_time and new_min >= 0):
                self.view.minimum_time = new_min
                self.time_slider.setRange(self.view.minimum_time * self.tps, self.tps * self.view.maximum_time)
                self.view.updateVecs()
        except ValueError:
            print("Value error in minText")

    def maxTextChanged(self):
        try:
            new_max = float(self.maxText.text() )
            if(new_max > self.view.minimum_time and new_max >= 0):
                self.view.maximum_time = new_max
                self.time_slider.setRange(self.view.minimum_time * self.tps, self.tps * self.view.maximum_time)
                self.view.updateVecs()
        except ValueError:
            print("Value error in maxText")

    def update(self):
        value = self.time_slider.value()
        new_val = value + 1
        if new_val <= self.tps * self.view.maximum_time:
            self.time_slider.setValue( int(new_val) )
        else:
            self.play_button.setText("Play")
            self.is_playing = False 
            self.timer.stop()
   
# Main creates an app with a scence that has a view that is our graphics view.
if __name__ == "__main__":

    app = QApplication(sys.argv)

    layout = Layout()
    layout.show()

    app.exec()
