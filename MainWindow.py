#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from TransController import tr
from PasswdController import PasswdController

class MainWindow(QtGui.QMainWindow):
    """
        MainWindow class represents main window.
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self._close_act = None
        
        self.initUI()
        self.createActions()
        self.createMenu()
        
    def initUI(self):
        """
            Initialize gui components. Create dock widgets.
        """
#         self.resize(300, 300)
        
        self.setWindowTitle(unicode("UserPass Manager alpha"))
        
        self.center()
        self.setDockOptions(QtGui.QMainWindow.AnimatedDocks | QtGui.QMainWindow.AllowNestedDocks)
        
        # create dock widgets, 1. Groups, 2. Passwords
        # groups
        self._groups_dw = QtGui.QDockWidget(tr("Groups"))
        self._groups_dw.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._groups_dw)
#         self._groups_vl = QtGui.QVBoxLayout()
#         self._groups_dw.setLayout(self._groups_vl)
        
        # create groups tree widget
        self._groups_tw = QtGui.QTreeWidget()
        # remove tree header
        self._groups_tw.header().close()
        self._groups_dw.setWidget(self._groups_tw)
#         self._groups_tw.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum))
        
        item = QtGui.QTreeWidgetItem()
        item.setText(0, tr("test"))
        
        item2 = QtGui.QTreeWidgetItem()
        item2.setText(0, tr("test2"))
        item2.setData(1, QtCore.Qt.DisplayRole, "dasdsad")
        
        self._groups_tw.addTopLevelItem(item)
        item.addChild(item2)
        
        # passwords
        self._passwords_dw = QtGui.QDockWidget(tr("Passwords"))
        self._passwords_dw.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self._passwords_dw)
        
        # create password dock central widget
        self._passwords_cw = QtGui.QWidget()
        self._passwords_dw.setWidget(self._passwords_cw)
        
        # create passwords layout
        self._passwords_vl = QtGui.QVBoxLayout()
        self._passwords_cw.setLayout(self._passwords_vl)
        
        # add table widget to passwords dock
        self._passwords_table = QtGui.QTableWidget()
        self._passwords_vl.addWidget(self._passwords_table)
        self._passwords_table.setColumnCount(len(PasswdController.getVisibleColumns()))
        
        # auto resize columns
        self._passwords_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._passwords_table.resizeColumnsToContents()
        
        # set column names
        self._passwords_table.setHorizontalHeaderLabels(PasswdController.getVisibleColumns())
        
    def createActions(self):
        """
            Initialize all actions, i.e. Close, Save etc.
        """
        # init close
        self._close_act = QtGui.QAction(tr("&Close"), self)
        self._close_act.setShortcuts(QtGui.QKeySequence.Close)
        self._close_act.setStatusTip(tr("Close application"))
        
        # connect to slot
        self._close_act.triggered.connect(QtCore.QCoreApplication.instance().quit)
        
        # init about action
        self._about_act = QtGui.QAction(tr("About"), self)
        self._about_act.setStatusTip(tr("About UserPass Manager"))
        
        self._about_act.triggered.connect(self.aboutDialog)
        
    def createMenu(self):
        """
            Initialize menu, add actions to menu.
        """
        # create menu bar
        menubar = QtGui.QMenuBar()
        self.setMenuBar(menubar)
        
        # create menu options and add actions
        file_menu = self.menuBar().addMenu(tr("&File"))
        file_menu.addAction(self._close_act)
        
        about_menu = self.menuBar().addMenu(tr("About"))
        about_menu.addAction(self._about_act)
        
    def center(self):
        """
            Center window.
        """
        # get frame geometry
        wg = self.frameGeometry()
        
        # get screen center
        cs = QtGui.QDesktopWidget().availableGeometry().center()
        wg.moveCenter(cs)
        
        self.move(wg.topLeft())
        
    def aboutDialog(self):
        QtGui.QMessageBox( QtGui.QMessageBox.Information, "About", "UserPass Manager v0.0.1 alpha\n\nSafely backup your credentials.").exec_()
        
        