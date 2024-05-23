"""
This file implements a Layout and Ribbon for the GUI, and the main function that will 
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
    QSpacerItem,
    QSizePolicy,
    QFileDialog,
    QDialogButtonBox,
    QToolButton,
    QDialog,
    QScrollArea,
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
    QShortcut,
    QKeySequence,
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
    QKeyCombination
    )

import os
# import test_network
import network_communication

import math
import json
import numpy as np # April 28, 2024 - After three months of developement, finally imported numpy

from qt_view import View 

class Layout(QWidget):

    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout(self)
        self.ribbon = QVBoxLayout(self)
     

        self.scene = QGraphicsScene(-1500, -1500, 3000, 3000)
        self.view = View(self.scene, self)
        
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

        self.editConfigAction = QAction("Edit Network Configuration", self.view)
        self.editConfigAction.triggered.connect(self.view.editNetworkConfig)


        fileMenu.addAction(self.editConfigAction)
        fileMenu.addSeparator()
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
            if(new_max > self.view.minimum_time and new_max >= 0 and new_max <= 1000):
                self.view.maximum_time = new_max
                self.time_slider.setRange(self.view.minimum_time * self.tps, self.tps * self.view.maximum_time)
                try:
                    self.view.updateVecs()
                except:
                    print("Uhoh")
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
   
