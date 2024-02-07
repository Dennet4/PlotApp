##########################################################################
# Copyright (c) 2022-2024 Reinhard Caspary                               #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

import math
#from fonttable import HP1345A
from .fonttable import HP1345A


class Font(object):

    _defaults = {
        "size": 5.0,
        "width": 5.0,
        "divisor": 1.0,
        "halign": "left",
        "valign": "base",
        "rotate": 0,
        "mirrorx": False,
        "mirrory": False,
        }

    _valid = {
        "halign": ("left", "center", "right"),
        "valign": ("top", "center", "base", "bottom"),
        }

    def __init__(self, table=None, **kwargs):

        # Store default parameters modified by kwargs
        self.defaults = {k: v for k, v in self._defaults.items()}
        self.defaults = self.parse(**kwargs)
        
        # Dictionary mapping unicode characters to a list of polylines
        if table is None:
            self.table = HP1345A
            self.defaults["divisor"] = 18.0
        else:
            self.table = table


    def parse(self, **kwargs):

        """ Return a parameter dictionary with kwargs merged into the
        font defaults. """
        
        args = {k: v for k, v in self.defaults.items()}
        for key, value in kwargs.items():
            if not key in args:
                raise RuntimeError("Unknown parameter '%s'!" % key)
            if key in self._valid:
                if isinstance(value, str):
                    value = value.lower()
                if value not in self._valid[key]:
                    raise RuntimeError("Invalid value '%s' for parameter %s!" % (value, key))
            args[key] = value
        return args
    

    def string(self, text, x0=0, y0=0, **kwargs):

        # Merge kwargs into the font parameters
        args = self.parse(**kwargs)

        # Polylines for the string scaled to font size
        scale = float(args["size"]) / args["divisor"]
        width = args["width"]
        lines = self.strokes(text, scale, width)
        #print("Init", self.bbox(lines))

        # Apply mirror
        if args["mirrorx"] and args["mirrory"]:
            lines = self.flop(lines, 2)
        elif args["mirrorx"]:
            lines = self.mirror(lines, "x")
        elif args["mirrory"]:
            lines = self.mirror(lines, "y")
        #print("Mirror", self.bbox(lines))

        # Determine bounding box
        bbox = self.bbox(lines)

        # Horizonal alignment offset
        if args["halign"] == "left":
            dx = -bbox[0]            
        elif args["halign"] == "right":
            dx = -bbox[2]
        else:
            dx = -0.5*(bbox[0] + bbox[2])

        # Vertical alignment offset
        if args["valign"] == "bottom":
            dy = -bbox[1]            
        elif args["valign"] == "top":
            dy = -bbox[3]
        elif args["valign"] == "base":
            dy = 0.0
        else:
            dy = -0.5*(bbox[1] + bbox[3])

        # Apply alignment offset
        if dx or dy:
            lines = self.shift(lines, dx, dy)
        #print("Align", self.bbox(lines))

        # Apply rotation
        angle = args["rotate"]
        if angle:
            lines = self.rotate(lines, angle)
        #print("Rotate", self.bbox(lines))

        # Apply global offset
        if x0 or y0:
            lines = self.shift(lines, x0, y0)
        #print("Global", self.bbox(lines))

        # Return list of polylines
        return lines


    def strokes(self, text, scale, width):

        lines = []
        for i, c in enumerate(text):

            # Space character
            if c == " ":
                continue

            # Unknown character
            if c not in self.table:
                raise RuntimeError("Unknown character code %04X!" % ord(c))

            # Add polylines of character
            x = i*width
            y = 0
            lines += self.char(c, x, y, scale)

        return lines


    def char(self, c, x0, y0, scale):

        lines = []
        for line in self.table[c]:
            line = [(x0+x*scale, y0+y*scale) for x, y in line]
            lines.append(line)
        return lines
                

    def bbox(self, lines):

        bbox = None
        for line in lines:
            for x, y in line:
                if bbox is None:
                    bbox = [x, y, x, y]
                else:
                    bbox[0] = min(bbox[0], x)
                    bbox[1] = min(bbox[1], y)
                    bbox[2] = max(bbox[2], x)
                    bbox[3] = max(bbox[3], y)
        return bbox


    def scale(self, lines, scale):

        newlines = []
        for line in lines:
            line = [(scale*x, scale*y) for x, y in line]
            newlines.append(line)
        return newlines


    def shift(self, lines, dx, dy):

        newlines = []
        for line in lines:
            line = [(x+dx, y+dy) for x, y in line]
            newlines.append(line)
        return newlines


    def rotate(self, lines, angle):

        # Rotate by multiples of 90 degrees
        if isinstance(angle, int) and angle % 90 == 0:
            num = (angle // 90) % 4
            if angle < 0:
                num = 4 - num
            return self.flip(lines, num)

        # Rotate by arbitrary angle
        sin = math.sin(angle*math.pi/180)
        cos = math.cos(angle*math.pi/180)
        newlines = []
        for line in lines:
            line = [(x*cos-y*sin, x*sin+y*cos) for x, y in line]
            newlines.append(line)
        return newlines


    def flip(self, lines, num):

        num = int(num) % 4
        if num == 0:
            return lines
        
        newlines = []
        for line in lines:
            if num == 1:
                line = [(-y, x) for x, y in line]
            if num == 2:
                line = [(-x, -y) for x, y in line]
            else:
                line = [(y, -x) for x, y in line]
            newlines.append(line)
        return newlines


    def mirror(self, lines, axis):

        axis = axis.lower()
        if axis not in ("x", "y"):
            raise RuntimeError("Unknown mirror axis '%s'!" % axis)

        horz = axis == "x"
        newlines = []
        for line in lines:
            if horz:
                line = [(-x, y) for x, y in line]
            else:
                line = [(x, -y) for x, y in line]
            newlines.append(line)
        return newlines


##########################################################################
if __name__ == "__main__":

    from tkinter import Tk, Canvas
    import time

    size = 50
    frame = 0.3 * size
    lw = 0.1*size

    t = time.strftime("%H:%M:%S", time.localtime())
    args = {
        "size": size,
        "width": size,
        "valign": "bottom",
        "mirrory": True,
        }
    f = Font(**args)
    lines = f.string("%s - Hello World!" % t, frame, frame)
    bbox = f.bbox(lines)
    
    w = Tk()
    width = bbox[2]-bbox[0] + 2*frame
    height = bbox[3]-bbox[1] + 2*frame
    c = Canvas(w, width=width, height=height)
    print(width, height)    

    for line in lines:
        for i in range(len(line)-1):
            x0, y0 = line[i]
            x1, y1 = line[i+1]
            if x0 == x1 and y0 == y1:
                x0 -= 0.5*lw
                y0 -= 0.5*lw
                x1 += 0.5*lw
                y1 += 0.5*lw
                c.create_oval(x0, y0, x1, y1, outline="", fill="red")
            else:
                c.create_line(x0, y0, x1, y1, capstyle="round", fill="red", width=lw)
            #print(x0, y0, x1, y1)
    c.pack()

    w.mainloop()
