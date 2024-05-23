"""
This file implements a Layout and Graphics View for the GUI, and the main function that will 
create and run that graphics view. it utilizes qt_node and qt_edge files.
It also utilizes the snn directory to get infromation from simualted networks. (i.e. make sure your sourced into pyframework)
"""
from PyQt6.QtWidgets import QApplication
from qt_layout import Layout
import sys

# Main creates an app with a scence that has a view that is our graphics view.
if __name__ == "__main__":

    app = QApplication(sys.argv)

    layout = Layout()
    layout.show()

    app.exec()
