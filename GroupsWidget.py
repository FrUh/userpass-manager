#!/usr/bin/python
#-*- coding: utf-8 -*-
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
import logging
from PyQt4 import QtGui, QtCore
from TransController import tr
from GroupController import GroupController
from IconController import IconController
from PasswdController import PasswdController

class GroupsWidget(QtGui.QTreeWidget):
    # public static attr:
    
    _TYPE_ALL = 1
    _TYPE_GROUP = 2
    _TYPE_PASS = 3
    
    # public signals:
    # first param: type, second: id
    # when on a group or password in group widget is clicked
    signalGroupSelChanged = QtCore.pyqtSignal(int, int)
    
    # param: password ID
    signalEditPasswd = QtCore.pyqtSignal(int)
    
    def __init__(self, parent = None):
        # private attr:
        self.__parent = parent
        self.__COL_ICON = 0
        self.__COL_NAME = 1
        self.__COL_ID = 2
        self.__COL_TYPE = 3
        self.__COL_GRP_ID = 4
        
        super(GroupsWidget, self).__init__(parent)
        
        self.initUI()
        if (self.__parent._user):
            self.initItems()
        self.initConections()
        
    def initConections(self):
        """
            Initialize all connections, handling events.
            
            @requires: initUI() first
        """
        # show password detail
        self.itemSelectionChanged.connect(self.showPasswords)
        
        # show edit dialog
        self.itemDoubleClicked.connect(self.editPasswd)
        
    def initUI(self):
        """
            Initialize groups tree widget, size etc.
        """
        logging.debug("Initialising UI components.")
        
        # remove header
        self.header().close()
        self.setColumnCount(2)
        # width for icon column
        self.setColumnWidth(0, 60)
        
        self.setMinimumWidth(170)
        
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def keyReleaseEvent(self, event):
        """
            Handle key released event, to edit password, when enter pressed.
        """
        logging.debug("key pressed: %d", event.key())
        
        if (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
            self.editPasswd()
        
    def editPasswd(self):
        """
            Emit signal if it is password.
        """
        item_id = self.currentItemData(self.__COL_ID)
        item_type = self.currentItemData(self.__COL_TYPE)
        
        # if is password selected
        if (item_type == self._TYPE_PASS):
            logging.debug("emitting password to edit ID: %d", item_id)
            
            self.signalEditPasswd.emit(item_id)
        else:
            logging.debug("not password to emit")
        
    def initItems(self):
        """
            Initialize groups tree items. Load items from DB.
        """
        logging.debug("Adding items to tree.")
        group_ctrl = GroupController(self.__parent._db_ctrl)
        passwd_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
        icon_ctrl = IconController(self.__parent._db_ctrl)
        
        groups = group_ctrl.selectAll()
        
        # group, that contains all passwords
        all_group = self.initItemData(icon_ctrl.selectByName("userpass")._icon, 
                                      tr("All"), -1, tr("All passwords group."), self._TYPE_ALL, -1)
        self.addTopLevelItem(all_group)
        
        # add cildren, all passwords to group all
        passwords = passwd_ctrl.selectByUserId(self.__parent._user._id)
        
        for passwd in passwords:
            child = self.initItemData(passwd._grp._icon._icon, passwd._title, passwd._id, passwd._comment, self._TYPE_PASS, passwd._grp._id)
            
            all_group.addChild(child)
        
        # insert groups to tree
        for group in groups:
            item = self.initItemData(group._icon._icon, tr(group._name), group._id, group._description, self._TYPE_GROUP, group._id)
            
            self.addTopLevelItem(item)
            
            # add cildren, all passwords to group all
            passwords = passwd_ctrl.selectByUserGrpId(self.__parent._user._id, group._id)
            
            for passwd in passwords:
                child = self.initItemData(passwd._grp._icon._icon, passwd._title, passwd._id, passwd._comment, self._TYPE_PASS, passwd._grp._id)
            
                item.addChild(child)
          
    def initItemData(self, icon, name, item_id, tooltip, item_type, item_grp_id):
        """
            Initialize item data.
            
            @param icon: item icon data
            @param name: item name
            @param item_id: item group
            @param tooltip: tooltip string
            @param item_type: item type (pass, group, all)
            
            @return: QTreeWidgetItem object
        """
        item = QtGui.QTreeWidgetItem()
        
        # load image to display mode
        pix = QtGui.QPixmap()
        pix.loadFromData(icon)
  
        item.setIcon(self.__COL_ICON, QtGui.QIcon(pix))
        item.setText(self.__COL_NAME, QtCore.QString.fromUtf8(tr(name)))
        item.setData(self.__COL_NAME, QtCore.Qt.ToolTipRole, QtCore.QString.fromUtf8(tr(tooltip)))
        item.setData(self.__COL_ID, QtCore.Qt.DisplayRole, item_id)
        item.setData(self.__COL_TYPE, QtCore.Qt.DisplayRole, item_type)
        item.setData(self.__COL_GRP_ID, QtCore.Qt.DisplayRole, item_grp_id)
        
        return item
      
    def showPasswords(self):
        """
            EMit signal to show item data.
        """
        self.currentItemData(self.__COL_NAME)
        
        item_id = self.currentItemData(self.__COL_ID)
        item_type = self.currentItemData(self.__COL_TYPE)
        
        logging.debug("emitting: type: %i, ID: %i", item_type, item_id)
        
        self.signalGroupSelChanged.emit(item_type, item_id)
        
              
    def currentItemData(self, col):
        """
            Get curent item type from __COL_TYPE
            
            @param col: column number
            
            @return: current item data col
        """
        c_item = self.currentItem()
        
        if (not c_item):
            logging.debug("item not selected")
            
            return False
        
        # to int return a tuple
        if (col == self.__COL_ID):
            ret = c_item.data(self.__COL_ID, QtCore.Qt.DisplayRole).toInt()[0]
            #.toInt()[0]
        
            logging.debug("curent item ID: %i", ret)
        elif (col == self.__COL_NAME):
            ret = c_item.data(self.__COL_NAME, QtCore.Qt.DisplayRole).toString()
            #tostring
        
            logging.debug("curent item name: %s", ret)
        elif (col == self.__COL_TYPE):
            ret = c_item.data(self.__COL_TYPE, QtCore.Qt.DisplayRole).toInt()[0]
            #.toInt()[0]
        
            logging.debug("curent item type: %i", ret)
            
        elif (col == self.__COL_GRP_ID):
            ret = c_item.data(self.__COL_GRP_ID, QtCore.Qt.DisplayRole).toInt()[0]
            #.toInt()[0]
        
            logging.debug("curent item group ID: %i", ret)
        return ret
    
    def currentItemGroupID(self):
        """
            Get current item group ID (DB ID)
            
            @return: if item has ID, return ID, otherwise False
        """
        g_id = self.currentItemData(self.__COL_GRP_ID)
        
        if (g_id and g_id >= 0):
            # has group ID
            return g_id
        else:
            return False
        
    def currentItemGroupName(self):
        """
            Return current item group name.
        """
        g_id = self.currentItemGroupID()
        
        if (g_id):
            group_ctrl = GroupController(self.__parent._db_ctrl)
            
            return group_ctrl.selectById(g_id)._name
        return False
        
    def deleteGroup(self, g_id):
        """
            Delete group with id. Delete cascade implemented on passwords.
            
            @param g_id: group id
        """
        logging.info("deleting group and chlidren password with ID: '%i'", g_id)
        
        group_ctrl = GroupController(self.__parent._db_ctrl)
        group_ctrl.deleteGroup(g_id)
        
    def currentPasswordTitle(self):
        """
            Get current password title.
            
            @return: password title, other False
        """
        item_type = self.currentItemData(self.__COL_TYPE)
        
        if (item_type == self._TYPE_PASS):
            title = self.currentItemData(self.__COL_NAME)
            
            logging.debug("current item title: %s", title)
            
            return title
        else:
            logging.debug("current item title: False")
            
            return False
        
    def currentPasswordId(self):
        """
            Get current password title.
            
            @return: password ID, other False
        """
        item_type = self.currentItemData(self.__COL_TYPE)
        
        if (item_type == self._TYPE_PASS):
            item_id = self.currentItemData(self.__COL_ID)
            
            logging.debug("current item ID: %s", item_id)
            
            return item_id
        else:
            return False
    
    def reloadItems(self):
        """
            Reloads data from DB.
        """
        self.clear()
        
        self.initItems()