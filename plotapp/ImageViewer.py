##########################################################################
# Copyright (c) 2023-2024 Reinhard Caspary and Dennet Orbaugh            #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################
#
# This module provides the class ImageViewer.
#
##########################################################################

import math

from PyQt5.QtGui import QPen, QPainter, QPixmap, QFont, QPolygonF, QColor, \
    QTransform, QMouseEvent
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QLineEdit, QLabel, QDialog, QComboBox, QPushButton, \
    QGraphicsView, QGraphicsPixmapItem, QGraphicsScene, QFormLayout, QVBoxLayout

from font import Font as LineFont


############################################################################
# ImageViewer
############################################################################

class ImageViewer(QGraphicsView):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setStyleSheet('background-color: white;')
        # Zoom towards the mouse cursor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # Disable scrollbars for the QGraphicsView
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Initialize variables
        self.window_size_x = 500
        self.window_size_y = 500
        self.window_pos_x = 0           # Afected by zoom
        self.window_pos_y = 0           # Afected by zoom
        self.window_pos_z = 1
        self.window_step = 25           # Afected by zoom
        self.margen_test = 0            # Test the margins
        self.data = data
        self.image_size = (100, 100)    # Afected by zoom
        # Initialize zoom factors
        self.zoom_factor_in = 4/3
        self.zoom_factor_out = 3/4
        self.zoom_factor = 1
        # Objects data
        self.objects_visible = False
        self.mouse_cooridnates = ["Mouse Coordinates",0]
        self.drawn_objects = [{
            'type': 'circle',
            'x': 250,
            'y': 250,
            'z': 0,
            'radius': 50,
            'color': "black",
            'linewidth': 2,
            'bounds': [200, 300, 300, 200]
        },
        {
            'type': 'circle',
            'x': 0,
            'y': 100,
            'z': 5,
            'radius': 100,
            'color': "black",
            'linewidth': 2,
            'bounds': [50, 50, 150, -50]
        },
        {
            'type': 'rectangle',
            'x': 200,  # X-coordinate of the rectangle's center
            'y': 200,  # Y-coordinate of the rectangle's center
            'z': 0,    # Z-coordinate (layer)
            'height': 80,  # Height of the rectangle
            'width': 120,  # Width of the rectangle
            'angle': 30,   # Rotation angle in degrees
            'color': "red",
            'linewidth': 2,
            'bounds': [135, 277.32, 265, 122.68]
        },
        {
            'type': 'line',
            'x': 300,  # X-coordinate of the line's starting point
            'y': 300,  # Y-coordinate of the line's starting point
            'z': 0,    # Z-coordinate (layer)
            'length': 100,  # Length of the line
            'angle': 0,    # Angle of the line in degrees
            'color': "blue",
            'linewidth': 2,
            'bounds': [300,400,300,300]
        },
        {
            'type': 'text',
            'content': "Hello : Init!",
            'x': 250,  # X-coordinate of the text's position
            'y': 250,  # Y-coordinate of the text's position
            'z': 0,    # Z-coordinate (layer)
            'letter_height': 20,  # Height of the text
            'angle': 0,           # Rotation angle in degrees
            'color': "green",
            'linewidth': 2,
            'bounds': [250, 508.66666666666663, 282.0, 250]
        }
        ]

        # Create the mouse_label
        self.mouse_label = QLabel(self)
        self.mouse_label.setStyleSheet('QLabel {color: black;}')
        self.mouse_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.mouse_label.setGeometry(5, 5, 250, 15)
        # Initial position of the mouse_label (adjust as needed)
        self.mouse_label.move(10, self.height() - 25)

        self.last_mouse_pos = None  # Store the last mouse position for panning

    def add_image(self, path, x, y, z):
        pixmap = QPixmap(path)
        #### HOTFIX
        size = (round(self.image_size[0]), round(self.image_size[1]))
        pixmap = pixmap.scaled(*size, Qt.KeepAspectRatio)  # Scale the pixmap

        image_item = self.scene.addPixmap(pixmap)
        image_item.setOffset(-self.image_size[0] / 2, -self.image_size[1] / 2)  # Offset based on Image_size
        image_item.setPos(x, y)

    def draw_circle(self, x, y, z, radius, color, linewidth):
        # Calculate Bounds [top, right, bot, left]
        bounds = [y - radius, x + radius, y + radius, x - radius]

        # Add circle information to the data structure
        self.drawn_objects.append({
            'type': 'circle',
            'x': x,
            'y': y,
            'z': z,
            'radius': radius,
            'color': color,
            'linewidth': linewidth,
            'bounds': bounds
        })

        self.update_camera_view()  # Trigger redraw

    def draw_rectangle(self, x, y, z, height, width, angle, color, linewidth):
        # Calculate the half dimensions of the rectangle
        half_height = height / 2
        half_width = width / 2

        # Calculate the angle in radians
        angle_rad = math.radians(angle)

        # Calculate the coordinates of the four corners of the rectangle
        x1 = x + half_width * math.cos(angle_rad) - half_height * math.sin(angle_rad)
        y1 = y + half_width * math.sin(angle_rad) + half_height * math.cos(angle_rad)

        x2 = x - half_width * math.cos(angle_rad) - half_height * math.sin(angle_rad)
        y2 = y - half_width * math.sin(angle_rad) + half_height * math.cos(angle_rad)

        x3 = x - half_width * math.cos(angle_rad) + half_height * math.sin(angle_rad)
        y3 = y - half_width * math.sin(angle_rad) - half_height * math.cos(angle_rad)

        x4 = x + half_width * math.cos(angle_rad) + half_height * math.sin(angle_rad)
        y4 = y + half_width * math.sin(angle_rad) - half_height * math.cos(angle_rad)

        # Calculate the bounds [top, right, bot, left]
        top = min(y1, y2, y3, y4)
        right = max(x1, x2, x3, x4)
        bot = max(y1, y2, y3, y4)
        left = min(x1, x2, x3, x4)

        # Add rectangle information to the data structure
        self.drawn_objects.append({
            'type': 'rectangle',
            'x': x,
            'y': y,
            'z': z,
            'height': height,
            'width': width,
            'angle': angle,
            'color': color,
            'linewidth': linewidth,
            'bounds': [top, right, bot, left]
        })

        self.update_camera_view()  # Trigger redraw

    def draw_line(self, x, y, z, length, angle, color, linewidth):
        # Calculate the angle in radians
        angle_rad = math.radians(angle)

        # Calculate the coordinates of the starting and ending points of the line
        x_start = x
        y_start = y
        x_end = x + length * math.cos(angle_rad)
        y_end = y + length * math.sin(angle_rad)

        # Calculate the bounds [top, right, bot, left]
        top = max(y_start, y_end)
        right = max(x_start, x_end)
        bot = min(y_start, y_end)
        left = min(x_start, x_end)

        # Add line information to the data structure
        self.drawn_objects.append({
            'type': 'line',
            'x': x,
            'y': y,
            'z': z,
            'length': length,
            'angle': angle,
            'color': color,
            'linewidth': linewidth,
            'bounds': [top, right, bot, left]
        })

        self.update_camera_view()  # Trigger redraw

    def draw_text(self, content, x, y, z, letter_height, angle, color, linewidth):
        # Calculate Bounding Box
        size = letter_height
        frame = 0.3 * size
        lw = 0.1*size

        args = {
            "size": size,
            "width": size,
            "valign": "bottom",
            "mirrory": True,
            }
        # Create an instance of your custom Font class
        custom_font = LineFont(**args)
        lines = custom_font.string(content, frame, frame)

        # Initialize bounding box coordinates
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        for line in lines:
            for char_x, char_y in line:
                # Update bounding box coordinates
                min_x = min(min_x, char_x)
                min_y = min(min_y, char_y)
                max_x = max(max_x, char_x)
                max_y = max(max_y, char_y)

        # Calculate the width and height of the bounding box
        bbox_width = max_x - min_x + 2 * frame
        bbox_height = max_y - min_y + 2 * frame

        # Calculate the bounds [top, right, bot, left]
        top = y
        right = x + bbox_width
        bot = y + bbox_height
        left = x

        # Add circle information to the data structure
        self.drawn_objects.append({
            'type': 'text',
            'content': content,
            'x': x,
            'y': y,
            'z': z,
            'letter_height': letter_height,
            'angle': angle,
            'color': color,
            'linewidth': linewidth,
            'bounds': [top, right, bot, left]
        })
        self.update_camera_view()  # Trigger redraw
        print("bounds: ",top, right, bot, left)

    # Draw X and Y axes
    def draw_axes(self):
        x_axis = QPen(Qt.blue)
        y_axis = QPen(Qt.blue)
        x_axis.setWidth(4)
        y_axis.setWidth(4)
        self.scene.addLine(0, self.height()/2, self.width(), self.height()/2, x_axis)
        self.scene.addLine(self.width()/2, 0, self.width()/2, self.height(), y_axis)

        font = QFont("Arial", 8)
        label_offset = 20  # Offset to position labels away from axes
        self.scene.addText("X", font).setPos(self.width() - label_offset, self.height() / 2 - label_offset)
        self.scene.addText("Y", font).setPos(self.width() / 2, label_offset)

        # Add numerical labels to X and Y axes
        step = self.window_step
        for i in range(int(0 + step), int(self.width() + step), step):
            x_coord = i + self.window_pos_x
            label = self.scene.addText(str(x_coord), font)
            label_width = label.boundingRect().width()
            label.setPos(i - label_width / 2, self.height() / 2 + label_offset)

        # Label Y-axis
        for i in range(int(step), int(self.height() - step), step):
            y_coord = i + self.window_pos_y  # Reverse the Y-coordinate direction
            label = self.scene.addText(str(y_coord), font)
            label.setPos(self.width()/2 - 1.5*label_offset , i)

    def draw_camera_frame(self):
        left_edge = QPen(Qt.black)
        top_edge = QPen(Qt.black)
        right_edge = QPen(Qt.black)
        bottom_edge = QPen(Qt.black)
        left_edge.setWidth(2)
        top_edge.setWidth(2)
        right_edge.setWidth(2)
        bottom_edge.setWidth(2)

        # Calculate the top-left corner of the camera view
        camera_view_x = (self.width() - self.window_size_x) / 2
        camera_view_y = (self.height() - self.window_size_y) / 2


        self.scene.addLine(
            camera_view_x,
            camera_view_y + self.window_size_y,
            camera_view_x + self.window_size_x,
            camera_view_y + self.window_size_y,
            top_edge
        )
        self.scene.addLine(
            camera_view_x,
            camera_view_y + self.window_size_y,
            camera_view_x,
            camera_view_y,
            left_edge
        )
        self.scene.addLine(
            camera_view_x,
            camera_view_y,
            camera_view_x + self.window_size_x,
            camera_view_y,
            bottom_edge
        )
        self.scene.addLine(
            camera_view_x + self.window_size_x,
            camera_view_y + self.window_size_y,
            camera_view_x + self.window_size_x,
            camera_view_y,
            right_edge
        )


        self.scene.addLine(self.margen_test, self.margen_test, self.margen_test, self.window_size_y-self.margen_test, QPen(Qt.red))
        self.scene.addLine(self.margen_test, self.margen_test, self.window_size_x-self.margen_test, self.margen_test, QPen(Qt.red))
        self.scene.addLine(self.margen_test, self.window_size_y -self.margen_test,  self.window_size_x-self.margen_test, self.window_size_y-self.margen_test, QPen(Qt.red))
        self.scene.addLine(self.window_size_x-self.margen_test, self.margen_test, self.window_size_x-self.margen_test, self.window_size_y-self.margen_test, QPen(Qt.red))

    # Update camera view with layers
    def update_camera_view(self):
        # Clear existing items from the scene
        self.scene.clear()
        # Clear existing images
        for item in self.scene.items():
            self.scene.removeItem(item)

#        self.draw_axes()  # Draw X and Y axes
#        self.draw_camera_frame()




        # Margins for the camera view
        left_margin = self.window_pos_x + self.margen_test
        right_margin = self.window_pos_x + self.window_size_x - self.margen_test
        lower_margin = self.window_pos_y + self.window_size_y - self.margen_test
        upper_margin = self.window_pos_y + self.margen_test
        front_margin = self.window_pos_z + 1

        # Sort images based on Z-value
        sorted_data = sorted(self.data.items(), key=lambda item: item[1]['z'])
        self.drawn_objects.sort(key=lambda obj: obj['z'])

        for key, options in sorted_data:
            imx_bounds = [coord * self.zoom_factor for coord in options['bounds']]
            if (left_margin < imx_bounds[1] and right_margin > imx_bounds[3] and
                    lower_margin > imx_bounds[0] and upper_margin < imx_bounds[2] and
                    options['z'] < front_margin):
                img_x = options['x'] * self.zoom_factor
                img_y = options['y'] * self.zoom_factor
                img_z = options['z']
                adjusted_x = img_x - self.window_pos_x  # Adjust image x position
                adjusted_y = img_y - self.window_pos_y  # Adjust image y position

                self.add_image(options['image_path'], int(adjusted_x), int(adjusted_y), int(img_z))

        # Create a QPixmap as a drawing surface
        pixmap = QPixmap(self.window_size_x, self.window_size_y)
        pixmap.fill(Qt.transparent) # Set the background to transparent


        # Create a QPainter object with the QPixmap as the paint device
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother shapes

        if self.objects_visible:
            # Draw drawn objects based on their type and parameters
            for obj in self.drawn_objects:
                if obj['type'] == 'circle':
                    # Check if the object is within the camera view
                    obj_bounds = [coord * self.zoom_factor for coord in obj['bounds']]
                    if (left_margin < obj_bounds[1] and right_margin > obj_bounds[3] and
                        lower_margin > obj_bounds[0] and upper_margin < obj_bounds[2] and
                        obj['z'] < front_margin):
                        obj_x = obj['x'] * self.zoom_factor
                        obj_y = obj['y'] * self.zoom_factor
                        obj_radius = obj['radius'] * self.zoom_factor
                        obj_color_str = obj['color']  # Get the color string
                        obj_color = QColor(obj_color_str)  # Create a QColor from the string
                        obj_linewidth = obj['linewidth']
                        adjusted_x = obj_x - self.window_pos_x  # Adjust image x position
                        adjusted_y = obj_y - self.window_pos_y  # Adjust image y position

                        # Draw the circle
                        painter.setPen(QPen(obj_color, obj_linewidth))
                        painter.drawEllipse(
                            (adjusted_x - obj_radius),
                            (adjusted_y - obj_radius),
                            (2 * obj_radius),
                            (2 * obj_radius)
                        )
                elif obj['type'] == 'rectangle':
                    obj_bounds = [coord * self.zoom_factor for coord in obj['bounds']]
                    if (left_margin < obj_bounds[1] and right_margin > obj_bounds[3] and
                        lower_margin > obj_bounds[0] and upper_margin < obj_bounds[2] and
                        obj['z'] < front_margin):

                        obj_x = obj['x'] * self.zoom_factor
                        obj_y = obj['y'] * self.zoom_factor
                        obj_height = obj['height'] * self.zoom_factor
                        obj_width = obj['width'] * self.zoom_factor
                        obj_angle = obj['angle']
                        obj_color_str = obj['color']  # Get the color string
                        obj_color = QColor(obj_color_str)  # Create a QColor from the string
                        obj_linewidth = obj['linewidth']

                        adjusted_x = obj_x - self.window_pos_x  # Adjust image x position
                        adjusted_y = obj_y - self.window_pos_y  # Adjust image y position

                        # Calculate the points for the rotated rectangle
                        rect = QPolygonF([
                            QPointF(-obj_width / 2, -obj_height / 2),
                            QPointF(obj_width / 2, -obj_height / 2),
                            QPointF(obj_width / 2, obj_height / 2),
                            QPointF(-obj_width / 2, obj_height / 2),
                        ])

                        # Create a transform for the rotation
                        rotation = QTransform()
                        rotation.translate(adjusted_x, adjusted_y)
                        rotation.rotate(obj_angle)
                        rotated_rect = rotation.map(rect)

                        # Draw the rotated rectangle
                        painter.setPen(QPen(obj_color, obj_linewidth))
                        painter.drawPolygon(rotated_rect)
                elif obj['type'] == 'line':
                    obj_bounds = [coord * self.zoom_factor for coord in obj['bounds']]
                    if (left_margin < obj_bounds[1] and right_margin > obj_bounds[3] and
                        lower_margin > obj_bounds[0] and upper_margin < obj_bounds[2] and
                        obj['z'] < front_margin):

                        obj_x = obj['x'] * self.zoom_factor
                        obj_y = obj['y'] * self.zoom_factor
                        obj_length = obj['length'] * self.zoom_factor
                        obj_angle = obj['angle']
                        obj_color_str = obj['color']  # Get the color string
                        obj_color = QColor(obj_color_str)  # Create a QColor from the string
                        obj_linewidth = obj['linewidth']

                        adjusted_x = obj_x - self.window_pos_x  # Adjust image x position
                        adjusted_y = obj_y - self.window_pos_y  # Adjust image y position

                        # Calculate the endpoint of the line based on length and angle
                        end_x = adjusted_x + obj_length * math.cos(obj_angle)
                        end_y = adjusted_y + obj_length * math.sin(obj_angle)

                        # Draw the line
                        painter.setPen(QPen(obj_color, obj_linewidth))
                        painter.drawLine(adjusted_x, adjusted_y, end_x, end_y)
                elif obj['type'] == 'text':
                    obj_bounds = [coord * self.zoom_factor for coord in obj['bounds']]
                    if (left_margin < obj_bounds[1] and right_margin > obj_bounds[3] and
                        lower_margin > obj_bounds[0] and upper_margin < obj_bounds[2] and
                        obj['z'] < front_margin):
                        obj_content = obj['content']
                        obj_x = obj['x'] * self.zoom_factor
                        obj_y = obj['y'] * self.zoom_factor
                        obj_letter_height = obj['letter_height'] * self.zoom_factor
                        obj_angle = obj['angle']
                        obj_color_str = obj['color']  # Get the color string
                        obj_color = QColor(obj_color_str)  # Create a QColor from the string
                        obj_linewidth = obj['linewidth']

                        adjusted_x = obj_x - self.window_pos_x  # Adjust image x position
                        adjusted_y = obj_y - self.window_pos_y  # Adjust image y position


                        size = obj_letter_height
                        frame = 0.3 * size
                        lw = 0.1*size

                        args = {
                            "size": size,
                            "width": size,
                            "valign": "bottom",
                            "mirrory": True,
                            }
                        # Create an instance of your custom Font class
                        custom_font = LineFont(**args)
                        lines = custom_font.string(obj_content, frame, frame)
                        #bbox = custom_font.bbox(lines)

                        #width = bbox[2] - bbox[0] + 2 * frame
                        #height = bbox[3] - bbox[1] + 2 * frame

                        for line in lines:
                            for i in range(len(line) - 1):
                                x0, y0 = line[i]
                                x1, y1 = line[i + 1]
                                if x0 == x1 and y0 == y1:
                                    x1 -= 0.5 * lw
                                    y1 -= 0.5 * lw
                                    x2 = x0 + 0.5 * lw
                                    y2 = y0 + 0.5 * lw
                                    painter.setPen(QPen(obj_color, obj_linewidth))
                                    #painter.drawEllipse(adjusted_x + x0, adjusted_y + y0, x1-x2,y1-y2)
                                    painter.drawPoint(adjusted_x + x0, adjusted_y + y0)
                                else:
                                    painter.setPen(QPen(obj_color, obj_linewidth))
                                    painter.drawLine(adjusted_x + x0, adjusted_y + y0, adjusted_x + x1, adjusted_y + y1)

        # End painting
        painter.end()

        # Create a QGraphicsPixmapItem and add it to the scene
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Update the view
        self.setSceneRect(pixmap_item.boundingRect())


    # Override keyPressEvent for camera view movement
    def keyPressEvent(self, event):
        # Handle arrow key presses
        if event.key() == Qt.Key_Left:
            self.window_pos_x = self.window_pos_x - self.window_step
            self.update_camera_view()
        elif event.key() == Qt.Key_Right:
            self.window_pos_x = self.window_pos_x + self.window_step
            self.update_camera_view()
        elif event.key() == Qt.Key_Up:
            self.window_pos_y = self.window_pos_y - self.window_step
            self.update_camera_view()
        elif event.key() == Qt.Key_Down:
            self.window_pos_y = self.window_pos_y + self.window_step
            self.update_camera_view()

    def zoom_in(self):
        self.zoom_factor *= self.zoom_factor_in
#        self.window_pos_x *= self.zoom_factor_in
#        self.window_pos_y *= self.zoom_factor_in
        self.image_size = (self.image_size[0] * self.zoom_factor_in, self.image_size[1] * self.zoom_factor_in)
        self.update_camera_view()

    def zoom_out(self):
        self.zoom_factor *= self.zoom_factor_out
#        self.window_pos_x *= self.zoom_factor_out
#        self.window_pos_y *= self.zoom_factor_out
        self.image_size = (self.image_size[0] * self.zoom_factor_out, self.image_size[1] * self.zoom_factor_out)
        self.update_camera_view()

    def go_to_home_view(self):
        # Reset window positions and zoom factor
        self.zoom_factor = 1
        self.image_size = (100, 100)
        x_max = 0
        x_min = 0
        y_max = 0
        y_min = 0
        sorted_data = sorted(self.data.items(), key=lambda item: item[1]['z'])

        for key, options in sorted_data:
            if options['z'] < self.window_pos_z:
                if options['x'] < x_min:
                    x_min = options['x']
                    if options['y'] < y_min:
                        y_min = options['y']
                    elif options['y'] > y_max:
                        y_max = options['y']
                elif options['x'] > x_max:
                    x_max = options['x']
                    if options['y'] < y_min:
                        y_min = options['y']
                    elif options['y'] > y_max:
                        y_max = options['y']
        self.window_pos_x = x_min + (x_max - x_min)/2
        self.window_pos_y = y_min + (y_max - y_min)/2
        while (x_min < self.window_pos_x - self.window_size_x) or (x_max > self.window_pos_x + self.window_size_x):
            self.zoom_out()
        while (y_min < self.window_pos_y - self.window_size_y) or (y_max > self.window_pos_y + self.window_size_y):
            self.zoom_out()
        self.update_camera_view()

    def draw_circle_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Circle")
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("color: black;")

        opt_layout = QFormLayout()
        x_input = QLineEdit()
        y_input = QLineEdit()
        z_input = QLineEdit()
        radius_input = QLineEdit()
        color_input = QLineEdit()
        linewidth_input = QLineEdit()
        opt_layout.addRow("Position X:", x_input)
        opt_layout.addRow("Position Y:", y_input)
        opt_layout.addRow("Position Z:", z_input)
        opt_layout.addRow("Radius:", radius_input)
        opt_layout.addRow("Color:", color_input)
        opt_layout.addRow("Linewidth:", linewidth_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(opt_layout)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            x = int(x_input.text())
            y = int(y_input.text())
            z = int(z_input.text())
            radius = int(radius_input.text())
            color = color_input.text()
            linewidth = int(linewidth_input.text())

            self.draw_circle(x,y,z,radius,color,linewidth)
            print(self.drawn_objects)

    def draw_rectangle_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Rectangle")
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("color: black;")
        opt_layout = QFormLayout()
        x_input = QLineEdit()
        y_input = QLineEdit()
        z_input = QLineEdit()
        height_input = QLineEdit()
        width_input = QLineEdit()
        angle_input = QLineEdit()
        color_input = QLineEdit()
        linewidth_input = QLineEdit()
        opt_layout.addRow("Position X:", x_input)
        opt_layout.addRow("Position Y:", y_input)
        opt_layout.addRow("Position Z:", z_input)
        opt_layout.addRow("Height:", height_input)
        opt_layout.addRow("Width:", width_input)
        opt_layout.addRow("Angle:", angle_input)
        opt_layout.addRow("Color:", color_input)
        opt_layout.addRow("Linewidth:", linewidth_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(opt_layout)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            x = int(x_input.text())
            y = int(y_input.text())
            z = int(z_input.text())
            height = int(height_input.text())
            width = int(width_input.text())
            angle = int(angle_input.text())
            color = color_input.text()
            linewidth = int(linewidth_input.text())

            self.draw_rectangle(x,y,z,height,width,angle,color,linewidth)
            print(self.drawn_objects)

    def draw_line_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Line")
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("color: black;")

        opt_layout = QFormLayout()
        x_input = QLineEdit()
        y_input = QLineEdit()
        z_input = QLineEdit()
        length_input = QLineEdit()
        angle_input = QLineEdit()
        color_input = QLineEdit()
        linewidth_input = QLineEdit()
        opt_layout.addRow("Position X:", x_input)
        opt_layout.addRow("Position Y:", y_input)
        opt_layout.addRow("Position Z:", z_input)
        opt_layout.addRow("Length:", length_input)
        opt_layout.addRow("Angle:", angle_input)
        opt_layout.addRow("Color:", color_input)
        opt_layout.addRow("Linewidth:", linewidth_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(opt_layout)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            x = int(x_input.text())
            y = int(y_input.text())
            z = int(z_input.text())
            length = int(length_input.text())
            angle = int(angle_input.text())
            color = color_input.text()
            linewidth = int(linewidth_input.text())

            self.draw_line(x,y,z,length,angle,color,linewidth)
            print(self.drawn_objects)

    def draw_text_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Rectangle")
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("color: black;")

        opt_layout = QFormLayout()
        content_input = QLineEdit()
        x_input = QLineEdit()
        y_input = QLineEdit()
        z_input = QLineEdit()
        height_input = QLineEdit()
        angle_input = QLineEdit()
        color_input = QLineEdit()
        linewidth_input = QLineEdit()
        opt_layout.addRow("Content:", content_input)
        opt_layout.addRow("Position X:", x_input)
        opt_layout.addRow("Position Y:", y_input)
        opt_layout.addRow("Position Z:", z_input)
        opt_layout.addRow("Letter height:", height_input)
        opt_layout.addRow("Angle:", angle_input)
        opt_layout.addRow("Color:", color_input)
        opt_layout.addRow("Linewidth:", linewidth_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(opt_layout)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            content = content_input.text()
            x = int(x_input.text())
            y = int(y_input.text())
            z = int(z_input.text())
            height = int(height_input.text())
            angle = int(angle_input.text())
            color = color_input.text()
            linewidth = int(linewidth_input.text())

            self.draw_text(content,x,y,z,height,angle,color,linewidth)
            print(self.drawn_objects)

    def add_object(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Object")
        dialog.setFixedSize(300, 200)
        dialog.setStyleSheet("color: black;")

        object_type_label = QLabel("Select Object Type:")
        object_type_combo = QComboBox()
        object_type_combo.addItem("Circle")
        object_type_combo.addItem("Rectangle")
        object_type_combo.addItem("Line")
        object_type_combo.addItem("Text")

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        layout = QFormLayout()
        layout.addRow(object_type_label, object_type_combo)
        layout.addRow(ok_button, cancel_button)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            selected_type = object_type_combo.currentText()

            if selected_type == "Circle":
                self.draw_circle_dialog()
            elif selected_type == "Rectangle":
                self.draw_rectangle_dialog()
            elif selected_type == "Line":
                self.draw_line_dialog()
            elif selected_type == "Text":
                self.draw_text_dialog()

    def object_visible(self, event):
        self.objects_visible = not self.objects_visible
        self.update_camera_view()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Print the mouse coordinates to the console
#        self.mouse_cooridnates = [int(self.window_pos_x + event.x()) , int(self.window_pos_y + event.y())]
        self.mouse_cooridnates = [int(self.window_pos_x + event.x()/self.zoom_factor) , int(self.window_pos_y + event.y()/self.zoom_factor)]
        self.mouse_label.setText(f"Mouse Coordinates: X={self.mouse_cooridnates[0]}, Y={self.mouse_cooridnates[1]}")
        print("Mouse Coordinates:", self.mouse_cooridnates, self.window_pos_x, self.window_pos_y, event.x(), event.y())
        if event.buttons() == Qt.LeftButton and self.lasst_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos

            # Calculate the relative movement and adjust window positions
            self.window_pos_x -= delta.x()
            self.window_pos_y -= delta.y()

            self.update_camera_view()

            self.last_mouse_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.last_mouse_pos is not None:
            self.last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15  # Number of 15-degree steps

        for _ in range(abs(int(num_steps))):
            if num_steps > 0:
                self.zoom_in()
            else:
                self.zoom_out()

    def resizeEvent(self, event):
        # Update the window_size_x whenever the widget is resized
        self.window_size_x = self.width()
        self.window_size_y = self.height()
        super().resizeEvent(event)
        # Update the position of the mouse_label when the viewer is resized
        self.mouse_label.move(10, self.height() - 25)
        self.update_camera_view()


