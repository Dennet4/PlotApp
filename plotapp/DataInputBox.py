##########################################################################
# Copyright (c) 2023-2024 Reinhard Caspary and Dennet Orbaugh            #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################
#
# This module provides the class DataInputBox.
#
##########################################################################

import os

from PyQt5.QtWidgets import QFileDialog, QLineEdit, QLabel, QComboBox, \
    QPushButton, QCheckBox, QWidget, QFormLayout

###### FIX THIS!
#from .files.qcheckcombobox import CheckComboBox
from .data_specifications import data_specifications
from .data_values import data_values
###### FIX THIS!


############################################################################
# DataInputBox
############################################################################

class DataInputBox(QWidget):
    def __init__(self, data_specifications, data_values, parent=None):
        self.last_loaded_file = None
        # Variable to track whether changes have been made
        self.changes_made = False
        super().__init__(parent)
        self.widget = QWidget(self)

        # Create a form layout for the widget
        self.layout = QFormLayout(self)

        # Create labels or input fields for each option
        self.widgets = {}  # Store references to widgets for later use

        # Add labels or input fields for each option
        for key, options in data_specifications.items():
            label = QLabel(options['name'])
            value = data_values.get(key, options['default'])  # Get the corresponding value from data_values dictionary

            if options['type'] == str:
                widget = QLineEdit(str(value))
                if options.get('writable', False):
                    widget.textChanged.connect(self.handle_text_change)
            elif options['type'] == int:
                widget = QLineEdit()
                widget.setText(str(value))
                if options.get('writable', False):
                    widget.textChanged.connect(self.handle_int_text_change)
            elif options['type'] == float:
                widget = QLineEdit()
                widget.setText(str(value))
                if options.get('writable', False):
                    widget.textChanged.connect(self.handle_float_text_change)
            elif options['type'] == bool:
                widget = QCheckBox()
                widget.setChecked(value)
                widget.stateChanged.connect(self.handle_checkbox_change)
            elif options['type'] == list:
                widget = QComboBox()
                widget.addItems(options['parameters'][0])
                widget.setCurrentText(value)
                widget.currentIndexChanged.connect(self.handle_dropdown_change)

            self.layout.addRow(label, widget)
            self.widgets[key] = widget


        # Add a button to save the values
        load_button = QPushButton("load")
        load_button.clicked.connect(self.load_values)
        self.layout.addRow(load_button)


        self.setLayout(self.layout)


    def update_display(self, data):
        for key, options in data_specifications.items():
            if key in self.widgets:
                widget = self.widgets[key]
                value = data['data_values'].get(key, options['default'])

                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)

    def update_values(self, data_values):
        for key, value in data_values.items():
            if key in self.widgets:
                widget = self.widgets[key]
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)

    def handle_text_change(self, text):
        sender = self.sender()
        key = self.get_key_from_widget(sender)
        if key is not None:
            options = data_specifications[key]

            if options.get('writable', False):
                value = text
                if options['type'] == int:
                    try:
                        value = int(text)
                    except ValueError:
                        sender.setStyleSheet("background-color: red;")
                        return

                sender.setStyleSheet("background-color: white;")
                data_values[key] = value  # Save the updated value to data_values

                self.changes_made = True # Set change flag to True
                print(self.changes_made)

    def handle_int_text_change(self, text):
        sender = self.sender()
        key = self.get_key_from_widget(sender)
        if key is not None:
            try:
                value = int(text)
                options = data_specifications[key]
                min_value = options['parameters'].get('min', float('-inf'))
                max_value = options['parameters'].get('max', float('inf'))
                if min_value <= value <= max_value:
                    sender.setStyleSheet("background-color: white;")
                    if options.get('writable', False):
                        data_values[key] = value  # Save the updated value to data_values
                        self.changes_made = True # Set change flag to True
                        print(self.changes_made)
                else:
                    sender.setStyleSheet("background-color: red;")
            except ValueError:
                sender.setStyleSheet("background-color: red;")

    def handle_float_text_change(self, text):
        sender = self.sender()
        key = self.get_key_from_widget(sender)
        if key is not None:
            options = data_specifications[key]

            if options.get('writable', False):
                try:
                    value = float(text)
                    min_value = options['parameters'].get('min', float('-inf'))
                    max_value = options['parameters'].get('max', float('inf'))
                    digits = options['parameters'].get('digits', None)

                    if min_value <= value <= max_value:
                        if digits is not None:
                            value_str = f"{value:.{digits}f}"
                            sender.setText(value_str)
                        sender.setStyleSheet("background-color: white;")
                        data_values[key] = value  # Save the updated value to data_values
                        self.changes_made = True # Set change flag to True
                        print(self.changes_made)
                    else:
                        sender.setStyleSheet("background-color: red;")
                except ValueError:
                    sender.setStyleSheet("background-color: red;")

    def handle_checkbox_change(self, state):
        sender = self.sender()
        selected_state = bool(state)
        if selected_state:
            sender.setStyleSheet("background-color: yellow;")
            self.changes_made = True # Set change flag to True
            print(self.changes_made)
        else:
            sender.setStyleSheet("background-color: white;")
            self.changes_made = True # Set change flag to True
            print(self.changes_made)

    def handle_dropdown_change(self, index):
        sender = self.sender()
        key = self.get_key_from_widget(sender)
        if key is not None:
            data_values[key] = sender.currentText()  # Save the updated value to data_values
            self.changes_made = True # Set change flag to True
            print(self.changes_made)

    # def handle_dropdown_change(self, index):
    #     sender = self.sender()  # Get the combobox that triggered the signal
    #     selected_value = sender.currentText()  # Retrieve the selected value
    #     print(f'Selected value: {selected_value}')

    def get_key_from_widget(self, widget):
        for key, value in self.widgets.items():
            if value is widget:
                return key
        return None

    def save_values(self):
        # Save the values to the data_values dictionary
        updated_data = self.get_updated_values()
        # Update the file in the "files" subfolder
        if self.last_loaded_file is None:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "data_values.py")
        else:
            file_path = self.last_loaded_file

        with open(file_path, 'w') as file:
            file.write(f"data_values = {updated_data}")
            self.changes_made = False
            print("Values saved successfully.")
            print(self.changes_made)

    def save_values_as(self):
        # Save the values to the data_values dictionary
        updated_data = self.get_updated_values()
        data_values.update(updated_data)
        # Open a file dialog to select the file to save the values
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Data Values", "", "Python Files (*.py)")
        if file_path:
            with open(file_path, 'w') as file:
                file.write(f"data_values = {updated_data}")
                self.changes_made = False
                print("Values saved successfully.")
                print(self.changes_made)

    def get_updated_values(self):
        updated_data = {}

        for key, widget in self.widgets.items():
            if key in data_specifications:
                options = data_specifications[key]

                if options.get('writable', False):
                    if isinstance(widget, QLineEdit):
                        value = widget.text()
                        updated_data[key] = int(value) if options['type'] == int else value
                    elif isinstance(widget, QCheckBox):
                        updated_data[key] = widget.isChecked()
                    elif isinstance(widget, QComboBox):
                        updated_data[key] = widget.currentText()

        return updated_data

    def load_values(self):
        # Open a file dialog to select the file to load the values
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Data Values", "", "Python Files (*.py)")

        if file_path:
            # Load the values from the selected file
            with open(file_path, 'r') as file:
                file_contents = file.read()
                # Create a dictionary to store the loaded values
                loaded_data = {}
                # Execute the file contents within the dictionary scope
                exec(file_contents, loaded_data)

            # Update the data_values dictionary with the loaded values
            data_values.update(loaded_data)
            # Update the input widgets with the loaded values
            self.update_values(loaded_data)
            # Update the display with the loaded values
            self.update_display(loaded_data)

            self.last_loaded_file = file_path

            print("Values loaded successfully from:", self.last_loaded_file)


# =============================================================================
#         # Create a combobox for data options
#     def OptionCombobox(self, data):
#         self.dataComboBox = CheckComboBox(placeholderText='Options')
#         model = self.dataComboBox.model()
#         for i, option in enumerate(data):
#             self.dataComboBox.addItem(option)
#             model.item(i).setCheckable(True)
#
#         # Create a widget to hold the layout
#         self.container = QWidget(self)
#         self.container.setStyleSheet('QWidget {background-color: white; color: black}')
#         self.container.setLayout(self.layout)
#
#         # Create a scroll area widget and set the layout to the container widget
#         self.scrollArea = QScrollArea(self)
#         self.scrollArea.setWidgetResizable(True)
#         self.scrollArea.setWidget(self.container)
#
#         # Set the widget as the central widget of the topRightContainer
#         self.container_layout = QVBoxLayout(self)
#         self.container_layout.addWidget(self.dataComboBox)
#         self.container_layout.addWidget(self.scrollArea)
#         self.setLayout(self.container_layout)
#
# =============================================================================


