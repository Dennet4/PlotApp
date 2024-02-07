##########################################################################
# Copyright (c) 2023-2024 Reinhard Caspary and Dennet Orbaugh            #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################
#
# This module provides the class MainWindow.
#
##########################################################################

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QToolBar, QMessageBox, QMainWindow, \
    QWidget, QHBoxLayout, QVBoxLayout, QAction

from .ImageViewer import ImageViewer
from .DataInputBox import DataInputBox
from .WarningBox import WarningBox

###### FIX THIS!
from .data_specifications import data_specifications
from .data_values import data_values
from .data_images import image_data
###### FIX THIS!

# Global parameters
MINSIZE = (500, 300)
#DEFAULT_STYLE = "background-color: white; color: black"


class MainWindow(QMainWindow):

    def __init__(self, app):
        
        """ Initialize the PlotApp main window. """

        # Initialize the parent class
        super().__init__()

        # Reference to the application
        self.app = app

        # Main window initialization
        self.setWindowTitle('PlotApp')
        #self.setStyleSheet(DEFAULT_STYLE)
        self.setWindowIcon(QIcon('images\icon.png'))

        # Initial window size
        screen = app.primaryScreen()
        size = screen.availableGeometry()
        w = round(max(MINSIZE[0], 0.8*size.width()))
        h = round(max(MINSIZE[1], 0.8*size.height()))
        self.resize(w, h)
        self.setMinimumSize(MINSIZE[0], MINSIZE[1])

        # Viewer widget
        self.viewer = ImageViewer(self, image_data)

        # Data box widget
        self.dataBox = DataInputBox(data_specifications, data_values, self)
        #self.dataBox.setMinimumWidth(200)
        #self.dataBox.setMaximumWidth(300)

        # Foot line widget
        self.footLine = WarningBox(self)
        #self.footLine.setMinimumHeight(20)

        # Initialize content for main window
        self.initCentralWidget()
        self.initMenuBar()
        self.initToolBar()


    def initCentralWidget(self):
        
        """ Create central widget with layout and content. """
        
        # Top layout
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.viewer)
        topLayout.addWidget(self.dataBox)
        #topLayout.setContentsMargins(10, 0, 10, 0)
        topLayout.setStretch(0, 1)
        topLayout.setStretch(1, 0)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(self.footLine)
        #mainLayout.setContentsMargins(2, 2, 2, 2)
        mainLayout.setStretch(0, 1)
        mainLayout.setStretch(1, 0)

        # Main widget
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)


    def initMenuBar(self):

        """ Create all menues in the menubar and connect them to actions. """

        # Menubar object
        menuBar = self.menuBar()

        # Menu "File"
        menu = QMenu('&File', self)
        menu.addAction(QAction('&Load profile', self,
                               shortcut='Ctrl+1',
                               triggered=self.dataBox.load_values))
        menu.addAction(QAction('&Save profile', self,
                               shortcut='Ctrl+s',
                               triggered=self.dataBox.save_values))
        menu.addAction(QAction('&Save profile as', self,
                               shortcut='Ctrl+2',
                               triggered=self.dataBox.save_values_as))
        menu.addSeparator()
        menu.addAction(QAction('E&xit', self,
                               shortcut='Ctrl+Q',
                               triggered=self.close))
        menuBar.addMenu(menu)

        # Menu "Action"
        menu = QMenu('&Action', self)
        menu.addAction(QAction('Detect layers', self,
                               shortcut='Ctrl+d'))
        menu.addAction(QAction('Add Object', self,
                               shortcut='Ctrl+a',
                               triggered=self.viewer.add_object))
        menuBar.addMenu(menu)

        # Menu "Configuration"
        menu = QMenu('&Configuration', self)
        menu.addAction(QAction('&System', self,
                               shortcut='Ctrl+3'))
        menu.addAction(QAction('&Setup', self,
                               shortcut='Ctrl+4'))
        menu.addAction(QAction('&Sample', self,
                               shortcut='Ctrl+5'))


    def initToolBar(self):

        """ Create all buttons in the toolbar and connect them to actions. """

        # Toolbar object
        toolbar = QToolBar()
        toolbar.setFixedHeight(20)

        # Toolbar buttons
        toolbar.addAction(QAction(QIcon(), 'Home', self,
                                  triggered=self.viewer.go_to_home_view))
        toolbar.addAction(QAction(QIcon(), 'zoom +', self,
                                  triggered=self.viewer.zoom_in))
        toolbar.addAction(QAction(QIcon(), 'zoom -', self,
                                  triggered=self.viewer.zoom_out))

        # Add toolbar to the main window
        self.addToolBar(Qt.TopToolBarArea, toolbar)



    def closeEvent(self, event):
        
        """ Close main window. """
        
        if self.dataBox.changes_made:
            reply = QMessageBox.question(self, 'Save Changes',
                                         'Do you want to save the changes?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                self.dataBox.save_values()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    '''
    # Create the zoom option for the image
    def zoomIn(self):
        # Get the current scale factor
        scale = self.viewer.transform().m11()
        max_size = 10
        # Increase the scale factor by 0.1, but limit to a maximum of 10x
        if scale * 1.1 <= max_size:
            self.viewer.scale(1.1, 1.1)

    def zoomOut(self):
        # Get the current scale factor
        scale = self.viewer.transform().m11()

        # Decrease the scale factor by 0.1, or set to 0.1 if resulting scale factor is smaller than 0.1
        scale /= 1.1
        if scale < 0.1:
            scale = 0.1

        # Set the new scale factor
        self.viewer.setTransform(QTransform.fromScale(scale, scale))

    # Add the Keybord events
    def keyPressEvent(self, event):
        # Move image with arrow keys
        if event.key() == Qt.Key_Left:
            self.viewer.move(self.viewer.x() - 10, self.viewer.y())
        elif event.key() == Qt.Key_Right:
            self.viewer.move(self.viewer.x() + 10, self.viewer.y())
        elif event.key() == Qt.Key_Up:
            self.viewer.move(self.viewer.x(), self.viewer.y() - 10)
        elif event.key() == Qt.Key_Down:
            self.viewer.move(self.viewer.x(), self.viewer.y() + 10)

    # Wheel Events
    def wheelEvent(self, event):
        # Check if the mouse cursor is inside the bounds of self.graphicsViewLayoutItem
        pos = event.pos()
        if self.graphicsViewLayoutItem.geometry().contains(pos):
            # If the mouse is inside the graphics view, perform the zoom in/out
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            # If the mouse is outside the graphics view, ignore the event
            super().wheelEvent(event)
    '''
    '''
    # Touchscreen Events
    def eventFilter(self, obj, event):
        # Zoom with touch events
        if event.type() == QEvent.TouchUpdate:
            touch1 = event.touchPoints()[0]
            touch2 = event.touchPoints()[1]
            currentDistance = QLineF(touch1.pos(), touch2.pos()).length()
            previousDistance = QLineF(touch1.lastPos(), touch2.lastPos()).length()
            if currentDistance > previousDistance:
                self.zoomIn()

    def event(self, event):
        if event.type() == QEvent.Gesture:
            pinch = event.gesture(Qt.PinchGesture)
            if pinch:
                if pinch.state() == Qt.GestureStarted:
                    self.lastScaleFactor = 1.0
                self.viewer.resize(self.viewer.width() * pinch.scaleFactor() / self.lastScaleFactor, self.viewer.height() * pinch.scaleFactor() / self.lastScaleFactor)
                self.lastScaleFactor = pinch.scaleFactor()
                return True

            pan = event.gesture(Qt.PanGesture)
            if pan:
                if pan.state() == Qt.GestureStarted:
                    self.lastPanPosition = self.imageWidget.pos()
                self.imageWidget.move(self.lastPanPosition + pan.delta().toPoint())
                return True

        return super().event(event)
    '''

############################################################################
# Main loop for testing
############################################################################

if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    
    def run():
        
        """ Run PlotApp in a function to call it inside Spyder. """
        app = QApplication(sys.argv)
        mainWindow = MainWindow(app)
        mainWindow.show()
        app.exec_()
    
    # Run PlotApp
    run()