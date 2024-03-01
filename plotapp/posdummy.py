# -*- coding: utf-8 -*-

import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

"""
Window Layout:
    
+--------------+-----------+---------------+
|              | Reference |     Values    |
+--------------+-----------+---------------+
| Stage x      |           |  24700.423 µm |
| Stage y      |           |   1345.234 µm |
| Stage z      |           | -32345.340 µm |
| DHM OPL      |           |   4730.2   µm |
| DHM Δt       |           |      0.63  ms |
| DHM Shutter  |           |     30        |
+--------------+-----------+---------------+
|              |   <set>   |  <abs><rel>   |
+--------------+-----------+---------------+
"""


class Position(object):
    
    def __init__(self):
        
        self.x0 = (random.random()*50000) - 25000
        self.y0 = (random.random()*50000) - 25000
        self.z0 = (random.random()*50000) - 25000
        self.m0 = (random.random()*4000) + 3000
        
    @property
    def xPosition(self) -> float:
        return self.x0 + random.gauss(0.0, 2.0)
        
    @property
    def yPosition(self) -> float:
        return self.y0 + random.gauss(0.0, 2.0)
        
    @property
    def zPosition(self) -> float:
        return self.z0 + random.gauss(0.0, 2.0)
        
    @property
    def oplMotorPosition(self) -> float:
        return self.m0
    
    @property
    def shutter(self) -> int:
        return 30
    
    @property
    def shutterTime(self) -> float:
        return 1e-3 * (self.shutter * 20.0 + 30.0)


class Window(QMainWindow):
    
    def __init__(self, position: Position):
        super().__init__()
        self.pos = position
        self.absolute = True
        self.x0 = None
        self.y0 = None
        self.z0 = None
        self.m0 = None
        
        self.win = self.initWindow()
        
        self.update()
        
    
    def initWindow(self):
        
        """ Window constructor. Initialize layout and return Qt window object. 
        Connect ButtonPressed events:
            <set> -> self.setReference()
            <abs> -> self.setAbsolute()
            <rel> -> self.setRelative()
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        self.central_widget.setLayout(layout)

        self.createTable()
        self.addButtonsToTable()
        

    def createTable(self):
        # Set number of rows and columns
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        
        # Hide row and column labels
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        
        # Set stretch to make the table occupy the whole window
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Set section resize mode for vertical header
        header = self.tableWidget.verticalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # First row fixed height
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Rest of the rows stretch
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Rest of the rows stretch

        # Set the initial sizes
        self.tableWidget.setRowHeight(0, 30)  # Fixed height for the first row
        self.tableWidget.setRowHeight(1, 100)
        self.tableWidget.setRowHeight(2, 50)
        self.tableWidget.setColumnWidth(0, 70)
        self.tableWidget.setColumnWidth(1, 125)
        self.tableWidget.setColumnWidth(2, 125)

        # Add labels to specific cells
        self.reference_title_label = QTableWidgetItem("Reference")
        self.values_title_label = QTableWidgetItem("Values")

        self.tableWidget.setItem(0, 1, self.reference_title_label)
        self.tableWidget.setItem(0, 2, self.values_title_label)


    def addButtonsToTable(self):
        # Button set Reference
        self.button_set = QPushButton("Set")
        self.button_set.clicked.connect(lambda: self.setReference())
        self.tableWidget.setCellWidget(2, 1, self.button_set)

        # Create a layout to hold the buttons
        self.buttonLayout = QHBoxLayout()

        # Button set Absolute
        self.button_abs = QPushButton("Abs")
        self.button_abs.clicked.connect(lambda: self.setAbsolute())
        self.buttonLayout.addWidget(self.button_abs)

        # Button set Relative
        self.button_rel = QPushButton("Rel")
        self.button_rel.clicked.connect(lambda: self.setRelative())
        self.buttonLayout.addWidget(self.button_rel)

        # Set the layout as the widget for the cell
        cellWidget = QWidget()
        cellWidget.setLayout(self.buttonLayout)
        self.tableWidget.setCellWidget(2, 2, cellWidget)

    
    def setReference(self):
        print(f"Button setReference clicked")
        self.x0 = self.pos.xPosition
        self.y0 = self.pos.yPosition
        self.z0 = self.pos.zPosition
        self.m0 = self.pos.oplMotorPosition
        self.absoute = False
        self.update()
    
    
    def setAbsolute(self):
        print(f"Button setAbsolute clicked")
        self.absolute = True
        self.update()
        
    
    def setRelative(self):
        print(f"Button setRelative clicked")
        if self.x0 is None:
            return
        self.absolute = False
        self.update()


    def update(self):
        
        """ Read current properties from position object and display them. """
        
        x = self.pos.xPosition
        y = self.pos.yPosition
        z = self.pos.zPosition
        m = self.pos.oplMotorPosition
        s = self.pos.shutter
        t = self.pos.shutterTime
        
        hasRef = self.x0 is not None

        if not hasRef or self.absolute:
            x0 = None
            y0 = None
            z0 = None
            m0 = None
        else:
            x0 = self.x0
            y0 = self.y0
            z0 = self.z0
            m0 = self.m0
            x -= self.x0
            y -= self.y0
            z -= self.z0
            m -= self.m0
        
        self.showContent(x0, y0, z0, m0, x, y, z, m, s, t, hasRef)
    
    
    def showContent(self, x0, y0, z0, w0, x, y, z, m, s, t, hasRef):
        
        """ Display given data in window. Gray out / deactivate the <rel>
        button if hasRef is False. """
        if not hasRef:
            self.button_rel.setVisible(False)
        else:
            self.button_rel.setVisible(True)

         # Create a list of lists containing labels and values for each cell
        items = [
            ['Stage x',  f'{x0:.3f} µm' if x0 is not None else '', f'{x:.3f} µm' if x is not None else ''],     # µm
            ['Stage y',  f'{y0:.3f} µm' if y0 is not None else '', f'{y:.3f} µm' if y is not None else ''],     # µm
            ['Stage z',  f'{z0:.3f} µm' if z0 is not None else '', f'{z:.3f} µm' if z is not None else ''],     # µm
            ['DHM OPL',  f'{w0:.3f} µm' if w0 is not None else '', f'{m:.3f} µm' if m is not None else ''],     # µm
            ['DHM Δt', '', f'{t:.3f} ms' if t is not None else ''],     # ms
            ['DHM Shutter', '', s]            # 
        ]

        cell_text = ''
        ref_text = ''   
        value_text = ''

        # Loop through the items and set the data in the table
        for label, ref, value in items:
            cell_text += f'{label}\n'
            ref_text += f'{ref}\n'
            value_text += f'{value}\n'

        # Create QTableWidgetItem for each string and set them in the table
        cell_item = QTableWidgetItem()
        ref_item = QTableWidgetItem()
        value_item = QTableWidgetItem()

        cell_item.setText(cell_text)
        ref_item.setText(ref_text)
        value_item.setText(value_text)

        self.tableWidget.setItem(1, 0, QTableWidgetItem(cell_text))  
        self.tableWidget.setItem(1, 1, QTableWidgetItem(ref_text))
        self.tableWidget.setItem(1, 2, QTableWidgetItem(value_text))

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    position = Position()
    window = Window(position)
    window.show()
    
    sys.exit(app.exec_())