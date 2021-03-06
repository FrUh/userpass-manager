#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    MIT License

    Copyright (c) 2013-2016 Frantisek Uhrecky

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
from PyQt4 import QtGui, QtCore
from TransController import tr
from GroupsWidget import GroupsWidget
from PasswordsWidget import PasswordsWidget
from DetailWidget import DetailWidget
from EditPasswdDialog import EditPasswdDialog
from NewPasswdDialog import NewPasswdDialog
from NewGroupDialog import NewGroupDialog
import logging
from UserController import UserController
import AppSettings
from EditGroupDialog import EditGroupDialog
import shutil
import InfoMsgBoxes

class MainWindow(QtGui.QMainWindow):
    """
        MainWindow class represents main window.
    """
    # public attr:
    _db_ctrl = None
    
    def __init__(self, db_ctrl, user = None):
        self._db_ctrl = db_ctrl
        self._user = user
        
        super(MainWindow, self).__init__()
        
        self._close_act = None
        
        self.initUI()
        self.createActions()
        self.createMenu()
        self.initConections()
        
    def closeEvent(self, event):
        """
            Do matters on close event. In example delete clipboard.
        """
        logging.debug("deleting clipboard")
        QtGui.QApplication.clipboard().clear()
        
        try:
            logging.info("removing tmp dir: '%s'", AppSettings.TMP_PATH)
            
            # remove tmp files
            shutil.rmtree(AppSettings.decodePath(AppSettings.TMP_PATH))
        except Exception as e:
            logging.exception(e)
            
            InfoMsgBoxes.showErrorMsg(e)
        
    def initUI(self):
        """
            Initialize gui components. Create dock widgets.
        """        
#         self.resize(300, 300)
        self.setWindowTitle("UserPass Manager " + AppSettings.APP_VERSION)
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
        self._detail_w = DetailWidget(self, self._passwords_table._show_pass)
        
        # add widgets to splitter
        self._passwd_splitter.addWidget(self._passwords_table)
        self._passwd_splitter.addWidget(self._detail_w)
        
        # set stretch factor for password table
        self._passwd_splitter.setStretchFactor(0, 1)
        
    def setUserReloadShow(self, username, master):
        """
            Load user from database and reload items.
        """
        user_ctrl = UserController(self._db_ctrl)
        
        username = str(username.toUtf8())
        master = str(master.toUtf8())
        
        self._user = user_ctrl.selectByNameMaster(username, master)
        
        if (self._user):
            self.reloadItems()
        else:
            logging.error("something wrong, can't log in user.")
        self.show()
        
    def initConections(self):
        """
            Initialize all connections, handling events.
            
            @requires: initUI() first
        """
        # create connection to update table view
        self._groups_tw.signalGroupSelChanged.connect(self._passwords_table.showPasswords)
        self._groups_tw.signalGroupSelChanged.connect(self._detail_w.handleTypePassword)
        self._passwords_table.signalShowDetailPasswd.connect(self._detail_w.setPassword)
        
        # show edit passwd dialog
        self._passwords_table.signalEditPasswd.connect(self.showEditPasswdDialog)
        self._groups_tw.signalEditPasswd.connect(self.showEditPasswdDialog)
        
        # enable/disable delete action, depends on selection type in tree widget
        self._groups_tw.signalGroupSelChanged.connect(self.enDisPassGrpActions)
        
        # enable/disable delete action with selection password talbe
        self._passwords_table.signalSelChangedTypeId.connect(self.enDisPassGrpActions)
        
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
        
        # displayed in groups tree
        self._new_passwd_g = QtGui.QAction(tr("New password"), self)
        self._new_passwd_g.setToolTip(tr("Add new password to DB"))
        
        self._new_passwd_g.triggered.connect(self.showNewPasswdDialog)
        
        # delete password action
        self._del_passwd = QtGui.QAction(tr("Delete"), self)
        self._del_passwd.setShortcuts(QtGui.QKeySequence.Delete)
        self._del_passwd.setToolTip(tr("Delete password from DB"))
        self._del_passwd.setDisabled(True)
        
        self._del_passwd.triggered.connect(self.deletePassword)
        
        # displayed in groups tree
        self._del_passwd_g = QtGui.QAction(tr("Delete password"), self)
        self._del_passwd_g.setToolTip(tr("Delete password from DB"))
        self._del_passwd_g.setDisabled(True)
        
        self._del_passwd_g.triggered.connect(self.deletePassword)
        
        # new group action
        self._new_group = QtGui.QAction(tr("New"), self)
        self._new_group.setToolTip(tr("Add new group to DB"))
        
        self._new_group.triggered.connect(self.showNewGroupDialog)
        
        # new group action in groups tree right click menu
        self._new_group_g = QtGui.QAction(tr("New group"), self)
        self._new_group_g.setToolTip(tr("Add new group to DB"))
        
        self._new_group_g.triggered.connect(self.showNewGroupDialog)
        
        # edit group action
        self._edit_group = QtGui.QAction(tr("Edit"), self)
        self._edit_group.setToolTip(tr("Edit selected group"))
        self._edit_group.setDisabled(True)
        
        self._edit_group.triggered.connect(self.showEditGroupDialog)
        
        # edit group action in groups tree right click menu
        self._edit_group_g = QtGui.QAction(tr("Edit group"), self)
        self._edit_group_g.setToolTip(tr("Edit selected group"))
        self._edit_group_g.setDisabled(True)
        
        self._edit_group_g.triggered.connect(self.showEditGroupDialog)
        
        # delete group in groups tree
        self._del_group = QtGui.QAction(tr("Delete"), self)
        self._del_group.setToolTip(tr("Delete group from DB"))
        self._del_group.setDisabled(True)
        
        self._del_group.triggered.connect(self.deleteGroup)
        
        # delete group displayed in groups tree
        self._del_group_g = QtGui.QAction(tr("Delete group"), self)
        self._del_group_g.setToolTip(tr("Delete group from DB"))
        self._del_group_g.setDisabled(True)
        
        self._del_group_g.triggered.connect(self.deleteGroup)
        
        # add to table actions
        self._passwords_table.addAction(self._new_passwd)
        self._passwords_table.addAction(self._del_passwd)
        
        # add to groups tree actions
        self._groups_tw.addAction(self._new_passwd_g)
        self._groups_tw.addAction(self._del_passwd_g)
        self._groups_tw.addAction(self._new_group_g)
        self._groups_tw.addAction(self._edit_group_g)
        self._groups_tw.addAction(self._del_group_g)
        
    def enDisPassGrpActions(self, item_type, item_id):
        """
            Disable delete password action.
        """
        if (item_type == self._groups_tw._TYPE_PASS):
            self._del_passwd.setEnabled(True)
            self._del_passwd_g.setEnabled(True)
        else:
            self._del_passwd.setEnabled(False)
            self._del_passwd_g.setEnabled(False)
        
        if (item_type == self._groups_tw._TYPE_GROUP):
            self._del_group.setEnabled(True)
            self._del_group_g.setEnabled(True)
            self._edit_group.setEnabled(True)
            self._edit_group_g.setEnabled(True)
        else:
            self._del_group.setEnabled(False)
            self._del_group_g.setEnabled(False)
            self._edit_group.setEnabled(False)
            self._edit_group_g.setEnabled(False)
        
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
        group_menu.addAction(self._new_group)
        group_menu.addAction(self._edit_group)
        group_menu.addAction(self._del_group)
        
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
        QtGui.QMessageBox(QtGui.QMessageBox.Information, tr("About"), tr("ABOUT_TEXT_1") + " " + AppSettings.APP_VERSION + "\n" + tr("ABOUT_TEXT_2") + """

MIT License

Copyright (c) 2013-2016 Frantisek Uhrecky

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""").exec_()
        
    def showEditPasswdDialog(self, p_id):
        """
            Show edit password dialog.
            
            @param p_id: password id to edit
        """
        edit_dialog = EditPasswdDialog(self, p_id, self._passwords_table._show_pass)
        edit_dialog.signalPasswdSaved.connect(self.reloadItems)
        
        edit_dialog.exec_()
        
    def showNewPasswdDialog(self):
        """
            Password dialog to add new password.
        """
        new_pass_dialog = NewPasswdDialog(self, self._groups_tw.currentItemGroupID(), self._passwords_table._show_pass)
        
        if (new_pass_dialog.exec_() == QtGui.QDialog.Accepted):
            # all done
            self.reloadItems()
        
    def showNewGroupDialog(self):
        """
            Group dialog to add new password.
        """
        new_group_dialog = NewGroupDialog(self)
        if (new_group_dialog.exec_() == QtGui.QDialog.Accepted):
            # all done
            self.reloadItems()
        
    def deletePassword(self):
        """
            Delete password from database.
        """
        # frist check tree widget
        title = self._groups_tw.currentPasswordTitle()
        p_id = self._groups_tw.currentPasswordId()

        # also chck in table widget
        if (not title):
            title = self._passwords_table.currentItemTitle()
            p_id = self._passwords_table.currentItemID()
        
        logging.debug("delete password title: %s, ID: %i", title, p_id)
        
        if (title != False):
            msg = QtGui.QMessageBox(QtGui.QMessageBox.Question, title ,tr("Do you want delete password '") 
                              + title + "'?")
            msg.addButton(QtGui.QMessageBox.Yes)
            msg.addButton(QtGui.QMessageBox.No)
            
            ret = msg.exec_()
            
            if (ret == QtGui.QMessageBox.Yes):
                # delete password
                self._passwords_table.deletePassword(p_id)
                self.reloadItems()
        logging.debug("Not password selected title: %s", title)
        
    def deleteGroup(self):
        """
            Delete group from database and also all passwords in this group, if foreign key are enabled.
        """
        # frist check tree widget
        title = self._groups_tw.currentItemGroupName()
        g_id = self._groups_tw.currentItemGroupID()
        
        logging.debug("delete group title: %s, ID: %i", title, g_id)
        
        if (title != False):
            msg = QtGui.QMessageBox(QtGui.QMessageBox.Question, title ,tr("Do you want delete group '") 
                              + title + "' and also containing passwords?")
            msg.addButton(QtGui.QMessageBox.Yes)
            msg.addButton(QtGui.QMessageBox.No)
            
            ret = msg.exec_()
            
            if (ret == QtGui.QMessageBox.Yes):
                # delete password
                self._groups_tw.deleteGroup(g_id)
                self.reloadItems()
        logging.debug("Not group selected title: %s", title)
        
    def showEditGroupDialog(self):
        """
            Edit selected group.
        """
        g_id = self._groups_tw.currentItemGroupID()
        
        if (g_id):
            # is group selected
            edit_group_dialog = EditGroupDialog(self, g_id)
            
            if (edit_group_dialog.exec_() == QtGui.QDialog.Accepted):
                # all done
                self.reloadItems()
            
    def reloadItems(self, p_id = -1):
        """
            Reload groups, passwords.
            
            @param p_id: password id to display, if is < 0, doesn't display
        """
        try:
            self._groups_tw.reloadItems()
            self._passwords_table.reloadItems()

            if (p_id >= 0):
                self._detail_w.setPassword(p_id)
            else:
                self._detail_w.setHidden(True)
        except Exception as e:
            logging.exception(e)
            
            InfoMsgBoxes.showErrorMsg(e)