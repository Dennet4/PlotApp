##########################################################################
# Copyright (c) 2023-2024 Reinhard Caspary and Dennet Orbaugh            #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################
#
# This package provides the application PlotApp.
#
##########################################################################

import sys
from PyQt5.QtWidgets import QApplication

from .MainWindow import MainWindow


def run():
    
    """ Run PlotApp. """
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    app.exec_()
