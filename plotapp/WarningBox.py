##########################################################################
# Copyright (c) 2023-2024 Reinhard Caspary and Dennet Orbaugh            #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################
#
# This module provides the class WarningBox.
#
##########################################################################

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout, QSizePolicy

###### FIX THIS!
#from .files.warnings import warnings
###### FIX THIS!


############################################################################
# WarningBox
############################################################################

class WarningBox(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the label that will hold the warnings
        self.label = QLabel(self)
        self.label.setWordWrap(False) # enable or disable word wrapping
        self.label.setStyleSheet('QLabel {color: black;}')
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # align text to the top-left corner
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Create a widget to hold the label
        self.widget = QWidget(self)
        self.widget.setStyleSheet('QWidget {background-color: white;}')

        # Create a vertical layout for the widget
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)

        # Set the widget as the scroll area's widget
        self.setWidgetResizable(True)
        self.setWidget(self.widget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set the size policy to expand as necessary
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the minimum and maximum height
        self.setMinimumHeight(20)
        self.setMaximumHeight(50)

        # Add the warnings
        self.add_warning('No WarningYou can adjust these values as needed to set a custom width for the widget. Note that the sizeHint() method of the widget will use these values to determine the recommended size of the widget, which will affect the size of the QScrollArea.')
        self.add_warning('Warning 1')
        self.add_warning('Warning 2')
        self.add_warning('Warning 3')
        self.add_warning('Warning 4')
        self.add_warning('Warning 5')
        self.add_warning('Warning 6')
        self.add_warning('Warning 7')
        self.add_warning('Warning 8')
        self.add_warning('Warning 9')
        self.add_warning('Warning 10')
        self.add_warning('Warning 11')
        self.add_warning('Warning 12')
        self.add_warning('Warning 13')
        self.add_warning('Warning 14')
        self.add_warning('Warning 15')
        self.add_warning('Warning 16')
        self.add_warning('Warning 17')
        self.add_warning('Warning 18')



    def add_warning(self, warning):
        # Append the new warning to the existing text and update the label
        current_text = self.label.text()
        new_text = current_text + '\n' + warning
        self.label.setText(new_text)

    def clear_warnings(self):
        # Clear the warning label
        self.label.setText('')


