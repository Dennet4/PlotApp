from PyQt5.QtWidgets import QWidget, QSlider, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class SliderWithDisplay(QWidget):
    def __init__(self, orientation):
        super().__init__()

        # Values definition
        self.precision = 3
        self.units = "um"
        self.values = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

        # Create a slider
        self.slider = QSlider(orientation)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.values) - 1)
        self.slider.setValue(self.values.index(100))  # Set default value to 100

        self.speed = f"{float(self.values[self.slider.value()]):.{self.precision}f}"

        # Create a QLineEdit for entering a speed
        self.speed_input = QLineEdit(self)
        self.speed_input.setText(self.speed)
        self.speed_input.setMaxLength(10)  # Limit the length to 10 characters
        # Calculate the width based on the font and characters
        font_metrics = self.speed_input.fontMetrics()
        self.speed_input_text_width = font_metrics.width('X'  * (2 + self.speed_input.maxLength()))
        self.speed_input.setFixedWidth(self.speed_input_text_width)
        # Create a QLineEdit for entering a speed unit
        self.speed_unit = QLineEdit(self)
        self.speed_unit.setText(self.units)
        self.speed_unit.setMaxLength(2)  # Limit the length to 2 characters
        # Calculate the width based on the font and characters
        self.speed_unit_text_width = font_metrics.width('X' * (2 + self.speed_unit.maxLength()))
        self.speed_unit.setFixedWidth(self.speed_unit_text_width)

        # Connect signals
        self.slider.valueChanged.connect(self.update_label_text)
        self.speed_input.editingFinished.connect(self.update_slider_from_input)

        # Create a container widget for the slider
        slider_container = QWidget(self)
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.addWidget(self.slider)
        slider_layout.setAlignment(Qt.AlignCenter)  # Center align the slider

        # Create a container widget for the speed input and unit
        speed_container = QWidget(self)
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.speed_unit)
        speed_container.setMaximumWidth(self.speed_input_text_width + self.speed_unit_text_width)

        # Create the main layout based on orientation
        if orientation == Qt.Horizontal:
            layout = QHBoxLayout(self)
            # Add the containers to the main layout
            layout.addWidget(slider_container)
            layout.addWidget(speed_container)
            
        elif orientation == Qt.Vertical:
            layout = QVBoxLayout(self)
            # Add the containers to the main layout
            layout.addWidget(speed_container)
            layout.addWidget(slider_container)

        # Set the layout for the widget
        self.setLayout(layout)

    def update_label_text(self, value):
        # Update the label text when the slider value changes
        self.speed = f"{float(self.values[value]):.{self.precision}f}"
        self.speed_input.setText(self.speed)

    def update_slider_from_input(self):
        # Function to change the slider after the text has been changed
        entered_text = self.speed_input.text()
        try:
            entered_value = float(entered_text)
            # Find the closest value in the values list
            closest_value = min(self.values, key=lambda x: abs(x - entered_value))
            # Set the value of the slider without triggering a valueChanged signal
            self.slider.blockSignals(True)
            self.slider.setValue(self.values.index(closest_value))
            self.slider.blockSignals(False) 
        except ValueError:
            # Handle non-float input
            pass