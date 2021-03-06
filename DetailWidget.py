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
from PasswdController import PasswdController
from TransController import tr
from GroupsWidget import GroupsWidget
import datetime

class DetailWidget(QtGui.QWidget):
    def __init__(self, parent = None, show_pass = False):
        self.__parent = parent
        self._show_pass = show_pass
        super(DetailWidget, self).__init__(parent)
        
        self.initUI()
        
    def initUI(self):
        """
            Initilize UI components.
        """
        layout_gl = QtGui.QGridLayout()
        self.setLayout(layout_gl)
        
        title_label = QtGui.QLabel("<b>" + tr("Title:") + "</b>")
        username_label = QtGui.QLabel("<b>" + tr("Username:") + "</b>")
        passwd_label = QtGui.QLabel("<b>" + tr("Password:") + "</b>")
        url_label = QtGui.QLabel("<b>" + tr("URL:")  + "</b>")
        c_date_label = QtGui.QLabel("<b>" + tr("Creation date:") + "</b>")
        m_date_label = QtGui.QLabel("<b>" + tr("Modification date:") + "</b>")
        e_date_label = QtGui.QLabel("<b>" + tr("Expiration date:") + "</b>")
        comment_label = QtGui.QLabel("<b>" + tr("Comment:") + "</b>")
        attachment_label = QtGui.QLabel("<b>" + tr("Attachment:") + "</b>")
        
        layout_gl.addWidget(title_label, 0, 0)
        layout_gl.addWidget(username_label, 1, 0)
        layout_gl.addWidget(passwd_label, 2, 0)
        layout_gl.addWidget(url_label, 3, 0)
        layout_gl.addWidget(c_date_label, 0, 2)
        layout_gl.addWidget(m_date_label, 1, 2)
        layout_gl.addWidget(e_date_label, 2, 2)
        layout_gl.addWidget(attachment_label, 4, 0)
        layout_gl.addWidget(comment_label, 5, 0)
        
        self.__title = QtGui.QLabel()
        self.__username = QtGui.QLabel()
        self.__passwd = QtGui.QLabel()
        self.__url = QtGui.QLabel()
        self.__c_date = QtGui.QLabel()
        self.__m_date = QtGui.QLabel()
        self.__e_date = QtGui.QLabel()
        self.__comment = QtGui.QTextEdit()
        self.__comment.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.__comment.setMaximumHeight(100)
        self.__comment.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        self.__attachment = QtGui.QLabel()
        
        layout_gl.addWidget(self.__title, 0, 1)
        layout_gl.addWidget(self.__username, 1, 1)
        layout_gl.addWidget(self.__passwd, 2, 1)
        layout_gl.addWidget(self.__url, 3, 1, 1, 3)
        layout_gl.addWidget(self.__c_date, 0, 3)
        layout_gl.addWidget(self.__m_date, 1, 3)
        layout_gl.addWidget(self.__e_date, 2, 3)
        layout_gl.addWidget(self.__attachment, 4, 1)
        layout_gl.addWidget(self.__comment, 5, 1, 1, 3)
        
        layout_gl.setColumnStretch(1, 1)
        layout_gl.setColumnStretch(3, 1)
        
        # hide, it is none passwd clicked
        self.setHidden(True)
        
    def setPassword(self, p_id):
        """
            Show password detail with id p_id.
            
            @param p_id: password ID
        """
        logging.debug("password details ID: %i", p_id)
        
        passwd_ctrl = PasswdController(self.__parent._db_ctrl, self.__parent._user._master)
        
        # select password
        passwd = passwd_ctrl.selectById(p_id)[0]
        
        if (not passwd):
            return
        
        self.__title.setText(QtCore.QString.fromUtf8(passwd._title))
        
        if (self._show_pass):
            self.__username.setText(QtCore.QString.fromUtf8(passwd._username))
            self.__passwd.setText(QtCore.QString.fromUtf8(passwd._passwd))
        else:
            self.__username.setText("******")
            self.__passwd.setText("******")
        self.__url.setText(QtCore.QString.fromUtf8(passwd._url))
        self.__c_date.setText(str(datetime.datetime.fromtimestamp(passwd._c_date).strftime("%Y-%m-%d %H:%M:%S")))
        self.__m_date.setText(str(datetime.datetime.fromtimestamp(passwd._m_date).strftime("%Y-%m-%d %H:%M:%S")))
        
        if (passwd._expire == "false"):
            self.__e_date.setText(tr("Never"))
        else:
            self.__e_date.setText(str(datetime.datetime.fromtimestamp(passwd._e_date).strftime("%Y-%m-%d %H:%M:%S")))
        self.__comment.setText(QtCore.QString.fromUtf8(passwd._comment))
        self.__attachment.setText(QtCore.QString.fromUtf8(passwd._att_name))
        
        # now show details
        self.setHidden(False)
        
    def clearDetails(self):
        """
            CLear displayed details.
        """
        self.__title.setText("")
        self.__username.setText("")
        self.__passwd.setText("")
        self.__url.setText("")
        self.__c_date.setText("")
        self.__m_date.setText("")
        self.__e_date.setText("")
        self.__comment.setText("")
        self.__attachment.setText("")
        
    def handleTypePassword(self, item_type, item_id):
        """
            Handle signal from GroupsWidget, if it is clicked on password show detail, else do nothing.
            
            @param item_type: source type password, group, all
            @param item_id: item id, i.e. password ID
        """
        logging.debug("handling type: %i ID: %i", item_type, item_id)
        
        if (item_type == GroupsWidget._TYPE_PASS):
            # is password
            self.setPassword(item_id)
        else:
            # clear detials
            self.clearDetails()
            
            # hide details
            self.setHidden(True)