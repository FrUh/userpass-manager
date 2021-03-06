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
import logging
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt
from PasswdController import PasswdController
from GroupsWidget import GroupsWidget
import AppSettings

class PasswordsWidget(QtGui.QTableWidget):
    # parameters are item ID
    signalShowDetailPasswd = QtCore.pyqtSignal(int)
    # when double clicked
    signalEditPasswd = QtCore.pyqtSignal(int)
    # when selection changed params: type = password, item id
    signalSelChangedTypeId = QtCore.pyqtSignal(int, int)
    
    def __init__(self, parent = None):
        self.__parent = parent
        self.__COL_TITLE = 0
        self.__COL_USERNAME = 1
        self.__COL_PASSWORD = 2
        self.__COL_URL = 3
        self.__COL_ID = 4
        
        # how password and username in visible form
        self._show_pass = False
        self._del_clipboard = None
        
        super(PasswordsWidget, self).__init__()
        
        self._del_clipboard = QtCore.QTimer(self)
        self._del_clipboard.setInterval(AppSettings.CLIPBOARD_LIVE_MSEC)
        self._del_clipboard.setSingleShot(True)
        
        self.initUI()
        self.initConections()
        
    def initUI(self):
        """
            Initialize UI components.
        """
        # set column count
        self.setColumnCount(len(PasswdController.getTableColumns()))
        
        # set column names
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(PasswdController.getTableColumns())
        
        # hide ID column
        self.hideColumn(self.__COL_ID)
        
        # auto resize columns
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setMovable(True)
        
        # not editable
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        
        self.setMinimumWidth(460)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def initConections(self):
        """
            Initialize all connections, handling events.
            
            @requires: initUI() first
        """
        # set connections for editing password
        self.cellDoubleClicked.connect(self.editPasswd)
        
        # emits when slection cganged so (clicked, arrow move)
        self.itemSelectionChanged.connect(self.callShowDetails)
        self.itemSelectionChanged.connect(self.emitSelChanged)
        
        # connect timer del clipboard
        self._del_clipboard.timeout.connect(self.deleteClipboard)
        
    def keyPressEvent(self, event):
        """
            Hanlde key press event, move acrros columns and rows.
        """
        if (event.key() == QtCore.Qt.Key_Left):
            # move left
            row = self.currentRow()
            col = self.currentColumn()
            
            # column count -1 beacause there is a one hidden column
            self.setCurrentCell(row, (col - 1) % (self.columnCount() - 1))
            
        elif (event.key() == QtCore.Qt.Key_Right):
            # move left
            row = self.currentRow()
            col = self.currentColumn()
            
            # column count -1 beacause there is a one hidden column
            self.setCurrentCell(row, (col + 1) % (self.columnCount() - 1))
            
        elif (event.key() == QtCore.Qt.Key_Up):
            # move left
            row = self.currentRow()
            col = self.currentColumn()
            
            # column count -1 beacause there is a one hidden column
            self.setCurrentCell((row - 1) % self.rowCount(), col)
            
        elif (event.key() == QtCore.Qt.Key_Down):
            # move left
            row = self.currentRow()
            col = self.currentColumn()
            
            # column count -1 beacause there is a one hidden column
            self.setCurrentCell((row + 1) % self.rowCount(), col)
        elif (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
            # Handle release event to edit password, whe enter is pressed.
            if (self.rowCount()):
                self.callEditPasswd()
            else:
                logging.info("empty table")
        elif (event.matches(QtGui.QKeySequence.Copy)):
            # copy data to clipboard
            logging.info("copy shortcut pressed")
            
            self.copyToClipBoard()
         
    def copyToClipBoard(self):
        """
            Copy data to clipboard from current cell. And clear clipboard after few seconds, AppSetting.CLIPBOARD_LIVE_MSEC
        """
        row = self.currentRow()
        col = self.currentColumn()
        
        logging.info("curent row: %i, column: %i", row, col)
        
        data = ""
        
        # first stop old timer to clear clipboard
        if (self._del_clipboard and self._del_clipboard.isActive()):
            logging.info("stopping old timer to delete clipboard")
            
            self._del_clipboard.stop()
        
        if (row >= 0 and col >= 0):
            if (col == self.__COL_USERNAME and not self._show_pass):
                # select username from DB
                pass_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
                p_id = self.currentItemID()
                
                passwd = pass_ctrl.selectById(p_id)[0]
                
                data = passwd._username
            elif (col == self.__COL_PASSWORD and not self._show_pass):
                # select password from DB
                pass_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
                p_id = self.currentItemID()
                
                passwd = pass_ctrl.selectById(p_id)[0]
                
                data = passwd._passwd
            else:
                item = self.item(row, col)
                data = str(item.text().toUtf8())
            # copy to clipboard
            QtGui.QApplication.clipboard().setText(QtCore.QString.fromUtf8(data))
            logging.debug("data to clipboard: '%s'", data)
            
            # delete clipboard after time
            self._del_clipboard.start()
            
            logging.info("clipboard will be cleared after %i seconds", AppSettings.CLIPBOARD_LIVE_MSEC / 1000)
    
    def deleteClipboard(self):
        """
            Security meaning. Delete clipboart after few seconds.
        """
        logging.info("deleting clipboard")
        
        QtGui.QApplication.clipboard().clear()
    def showAll(self):
        """
            Show all passwords.
        """        
        passwd_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
        passwords = passwd_ctrl.selectByUserId(self.__parent._user._id)
        
        self.fillTable(passwords)
        
    def reloadItems(self):
        """
            Reload items from DB.
        """
        self.removeAllRows()
        
        self.showAll()
        
    def fillTable(self, passwords):
        """
            Insert passwords to table.
            
            @param passwords: passwords list
        """
        # disable sorting
        self.setSortingEnabled(False)
            
        # now fill passwords table view
        for passwd in passwords:
            if (not passwd):
                continue
            row = self.rowCount()
            logging.debug("adding password: %s , at row: %i", passwd, row)
            self.insertRow(row)
       
            pix = QtGui.QPixmap()
            pix.loadFromData(passwd._grp._icon._icon)
       
            # set data
            self.setItem(row, self.__COL_TITLE, QtGui.QTableWidgetItem((QtGui.QIcon(pix)), QtCore.QString.fromUtf8(passwd._title)))
            
            if (self._show_pass):
                # have to show pass username in visible form
                self.setItem(row, self.__COL_USERNAME, QtGui.QTableWidgetItem(QtCore.QString.fromUtf8(passwd._username)))
                self.setItem(row, self.__COL_PASSWORD, QtGui.QTableWidgetItem(QtCore.QString.fromUtf8(passwd._passwd)))
            else:
                # show as stars
                self.setItem(row, self.__COL_USERNAME, QtGui.QTableWidgetItem("******"))
                self.setItem(row, self.__COL_PASSWORD, QtGui.QTableWidgetItem("******"))
            self.setItem(row, self.__COL_URL, QtGui.QTableWidgetItem(QtCore.QString.fromUtf8(passwd._url)))
            self.setItem(row, self.__COL_ID, QtGui.QTableWidgetItem(str(passwd._id)))
        # enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(self.__COL_TITLE, Qt.AscendingOrder)
        
    def showPasswords(self, item_type, item_id):
        """
            Public slot to show passwords in table, whe signal emitPasswords(int, int)
            is emited.
            
            @param item_type: type of selected item (group, password, all)
            @param item_id: unique id from DB
        """
        # first remove all items
        self.removeAllRows()

        logging.info("signal: type: %i, ID: %i", item_type, item_id)
        passwd_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
        
        # detect type
        if (item_type == GroupsWidget._TYPE_ALL):
            # select all
            passwords = passwd_ctrl.selectByUserId(self.__parent._user._id)
        elif (item_type == GroupsWidget._TYPE_GROUP):
            #select by group
            passwords = passwd_ctrl.selectByUserGrpId(self.__parent._user._id, item_id)
        elif (item_type == GroupsWidget._TYPE_PASS):
            #select just one password
            passwords = passwd_ctrl.selectById(item_id)
        self.fillTable(passwords)
    
    def removeAllRows(self):
        """
            Remove all items from table.
        """
        # disable sorting
        self.setSortingEnabled(False)
        
        for i in range(0, self.rowCount()):
            i
            self.removeRow(self.rowCount() - 1)
            
    def showDetails(self, row, column):
        """
            Emits signal to show details about password.
            
            @param row: row index in table
            @param column: column index in table
        """
        item = self.item(row, self.__COL_ID)
        
        if item:
            p_id = item.text().toInt()[0]
            logging.info("item selection changed at item row: %i, column: %i, emiting ID: %i", row, column, p_id)
        
            self.signalShowDetailPasswd.emit(p_id)
        else:
            logging.info("no item selected")
        
    def editPasswd(self, row, column):
        """
            Emits signal to edit password.
            
            @param row: row index in table
            @param column: column index in table
        """
        logging.info("double clicked or enter pressed at item row: %i, column: %i", row, column)
        
        self.signalEditPasswd.emit(self.item(row, self.__COL_ID).text().toInt()[0])
        
    def callShowDetails(self):
        """
            Call showDetails().
        """
        self.showDetails(self.currentRow(), self.currentColumn())
        
    def callEditPasswd(self):
        """
            Call editPasswd().
        """
        self.editPasswd(self.currentRow(), self.currentColumn())
        
    def currentItemTitle(self):
        """
            Get current item title.
            
            @return: on succed Title string, else False
        """
        row = self.currentRow()
        item = self.item(row, self.__COL_TITLE)
        
        if (item):
            item_text = str(item.text().toUtf8())
            logging.info("curent item title: %s", item_text)
            
            return str(item_text)
        
        logging.info("item: %s", item)
        return False
    
    def currentItemID(self):
        """
            Get current item password ID.
            
            @return: on succed ID, else False
        """
        row = self.currentRow()
        item = self.item(row, self.__COL_ID)
        
        if (item):
            return item.text().toInt()[0]
        return False
    
    def emitSelChanged(self):
        """
            When selection changed, and is item selected, emit signal.
        """
        if (self.currentItemTitle()):
            self.signalSelChangedTypeId.emit(GroupsWidget._TYPE_PASS, self.currentItemID())
    
    def deletePassword(self, p_id):
        """
            Delete password from DB. And reloads items.
            
            @param p_id: password ID
        """
        logging.info("deleting password with id: %i", p_id)
        
        passwd_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
        passwd_ctrl.deletePassword(p_id)
        
        # now reload items
#         self.reloadItems()