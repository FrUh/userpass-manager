#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from TransController import tr
from GroupsWidget import GroupsWidget
from PasswordsWidget import PasswordsWidget
from DetailWidget import DetailWidget
from EditPasswdDialog import EditPasswdDialog
from UserModel import UserModel
from NewPasswdDialog import NewPasswdDialog
import logging

class MainWindow(QtGui.QMainWindow):
    """
        MainWindow class represents main window.
    """
    # public attr:
    _db_ctrl = None
    
    def __init__(self, db_ctrl):
        self._db_ctrl = db_ctrl
        
        super(MainWindow, self).__init__()
        
        self._close_act = None
        
        self.loginUser("fero", "heslo")
        self.initUI()
        self.createActions()
        self.createMenu()
        self.initConections()
        
        
    def initUI(self):
        """
            Initialize gui components. Create dock widgets.
        """
#         self.resize(300, 300)
        self.setWindowTitle("UserPass Manager alpha")
        self.resize(1000, 600)
        self.center()
        
        # create main splitter, splits passwords table and gorups
        self._main_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.setCentralWidget(self._main_splitter)
        
        # create groups widget with label, and groups
        groups_mw = QtGui.QWidget()
        groups_vl = QtGui.QVBoxLayout()
        
        groups_mw.setLayout(groups_vl)
        
        # create label
        groups_label = QtGui.QLabel("<b>" + tr("Groups") + "</b>")
        groups_vl.addWidget(groups_label)
        
        # create groups tree widget
        self._groups_tw = GroupsWidget(self)
        
        groups_vl.addWidget(self._groups_tw)

        self._main_splitter.addWidget(groups_mw)
        
        # create password central widget
        self._passwords_cw = QtGui.QWidget()
        self._main_splitter.addWidget(self._passwords_cw)
        self._main_splitter.setStretchFactor(1, 1)
        
        # create passwords layout, will contain passwords table and detail widget with spliter
        self._passwords_vl = QtGui.QVBoxLayout()
        self._passwords_cw.setLayout(self._passwords_vl)
        
        # add table widget
        self._passwords_table = PasswordsWidget(self)
        
        # create password and detail splitter
        self._passwd_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        
        # create label
        passwdords_label = QtGui.QLabel("<b>" + tr("Passwords") + "</b>")
        self._passwords_vl.addWidget(passwdords_label)
        
        # add splitter to layout
        self._passwords_vl.addWidget(self._passwd_splitter)
        
        # create detail widget
        self._detail_w = DetailWidget(self)
        
        # add widgets to splitter
        self._passwd_splitter.addWidget(self._passwords_table)
        self._passwd_splitter.addWidget(self._detail_w)
        
        # set stretch factor for password table
        self._passwd_splitter.setStretchFactor(0, 1)
        
    def initConections(self):
        """
            Initialize all connections, handling events.
            
            @requires: initUI() first
        """
        # create connection to update table view
        self._groups_tw.signalGroupSelChanged.connect(self._passwords_table.showPasswords)
        self._groups_tw.signalGroupSelChanged.connect(self._detail_w.handleType)
        self._passwords_table.signalShowDetailPasswd.connect(self._detail_w.setPassword)
        
        # show edit passwd dialog
        self._passwords_table.signalEditPasswd.connect(self.showEditPasswdDialog)
        self._groups_tw.signalEditPasswd.connect(self.showEditPasswdDialog)
        
    def createActions(self):
        """
            Initialize all actions, i.e. Close, Save etc.
        """
        # init close
        self._close_act = QtGui.QAction(tr("&Close"), self)
        self._close_act.setShortcuts(QtGui.QKeySequence.Close)
        self._close_act.setToolTip(tr("Close application"))
        
        # connect to slot
        self._close_act.triggered.connect(QtCore.QCoreApplication.instance().quit)
        
        # init about action
        self._about_act = QtGui.QAction(tr("About"), self)
        self._about_act.setToolTip(tr("About UserPass Manager"))
        
        self._about_act.triggered.connect(self.aboutDialog)
        
        # new password action
        self._new_passwd = QtGui.QAction(tr("New"), self)
        self._new_passwd.setShortcuts(QtGui.QKeySequence.New)
        self._new_passwd.setToolTip(tr("Add new password to DB"))
        
        self._new_passwd.triggered.connect(self.showNewPasswdDialog)
        
        # new password action
        self._del_passwd = QtGui.QAction(tr("Delete"), self)
        self._del_passwd.setShortcuts(QtGui.QKeySequence.Delete)
        self._del_passwd.setToolTip(tr("Delte password from DB"))
        
        self._del_passwd.triggered.connect(self.deletePassword)
        
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
        
        password_menu = self.menuBar().addMenu(tr("Password"))
        password_menu.addAction(self._new_passwd)
        password_menu.addAction(self._del_passwd)
        
        group_menu = self.menuBar().addMenu(tr("Group"))
        
        settings_menu = self.menuBar().addMenu(tr("Settings"))
        
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
        
    def showEditPasswdDialog(self, p_id):
        """
            Show edit password dialog.
            
            @param p_id: password id to edit
        """
        edit_dialog = EditPasswdDialog(self, p_id)
        edit_dialog.signalPasswdSaved.connect(self.reloadItems)
        
        edit_dialog.exec_()
        
    def showNewPasswdDialog(self):
        """
            Password dialog to add new password.
        """
        new_pass_dialog = NewPasswdDialog(self)
        new_pass_dialog.signalPasswdSaved.connect(self.reloadItems)
        
        new_pass_dialog.exec_()
        
    def deletePassword(self):
        """
            Delete password from database.
        """
        title = self._passwords_table.currentItemTitle()
        p_id = self._passwords_table.currentItemID()
        
        logging.debug("delete password title: %s, ID: %i", title, p_id)
        
        if (title):
            msg = QtGui.QMessageBox(QtGui.QMessageBox.Question, title ,tr("Do you want delete password '") 
                              + title + "'?")
            msg.addButton(QtGui.QMessageBox.Yes)
            msg.addButton(QtGui.QMessageBox.No)
            
            ret = msg.exec_()
            
            if (ret == QtGui.QMessageBox.Yes):
                # delete password
                self._passwords_table.deletePassword(p_id)
                
        
    def reloadItems(self, p_id = -1):
        """
            Reload groups, passwords.
            
            @param p_id: password id to display, if is < 0, doesn't display
        """
        self._groups_tw.reloadItems()
        self._passwords_table.reloadItems()
        
        if (p_id >= 0):
            self._detail_w.setPassword(p_id)
        else:
            self._detail_w.setHidden(True)
        
    def loginUser(self, username, master):
        """
            Log in user with master password.
        """
        self._user = UserModel(2, username, "heslo", "salt", master)