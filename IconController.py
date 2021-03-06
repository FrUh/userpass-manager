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
import sqlite3
import logging
from IconModel import IconModel
import AppSettings

class IconController:
    """
        Provides manipulating icons in database.
    """
    def __init__(self, db_controller):
        self._db_ctrl = db_controller
        self._connection = db_controller._connection
        self._cursor = db_controller._cursor
    
    def selectAll(self):
        """
            Select all icons from table Icons.
            @return: rows touple of dictionaries
        """
        try:
            self._cursor.execute("SELECT * FROM Icons;")
            rows = self._cursor.fetchall()        
            
            logging.info("icons selected: %i", len(rows))
        except sqlite3.Error as e:
            logging.exception(e)
            
            raise e
        finally:
            icons = []
            
            for row in rows:
                icons.append(self.createIconObj(row))
            return icons
        
    def selectById(self, i_id):
        """
            Search icon by id.
            @param i_id: icon id
            @return: row
        """
        try:
            self._cursor.execute("SELECT * FROM Icons WHERE id = :id;", {"id" : i_id})
            row = self._cursor.fetchone()
            
            if (row):
                count = 1
            else:
                count = 0
            
            logging.info("icons selected: %i", count)
        except sqlite3.Error as e:
            logging.exception(e)
            
            raise e
        finally:
            return self.createIconObj(row)
        
    def selectByName(self, name):
        """
            Search icon by name.
            @param name: icon name
            @return: row
        """
        try:
            self._cursor.execute("SELECT * FROM Icons WHERE name = :name;", {"name" : name})
            row = self._cursor.fetchone()
            
            if (row):
                count = 1
            else:
                count = 0
            
            logging.info("icons selected: %i", count)
        except sqlite3.Error as e:
            logging.exception(e)
            
            raise e
        finally:
            return self.createIconObj(row)
    
    def insertIcon(self, name, icon_path):
        """
            Insert icon in table Icons.
            
            @param name: icon name
            @param icon_path: path to icon
        """
        # open and read icon
        icon = self.readImage(icon_path)
        
        try:
            self._cursor.execute("INSERT INTO Icons(name, icon) VALUES(:name, :icon)",
                                  {"name" : name, "icon" : icon})
            self._connection.commit()
            
            logging.info("icons with ID: %i, inserted: %i, path to icon: %s", self._cursor.lastrowid, self._cursor.rowcount, icon_path)
        except sqlite3.IntegrityError as e:
            logging.warning(e)
            
            self._connection.rollback()
        except sqlite3.Error as e:
            logging.exception(e)
            
            self._connection.rollback()
            raise e
           
    def updateIcon(self, i_id, name, icon_path):
        """
            Updates icon with id.
            @param i_id: icon id
            @param name: icon name
            @param icon_path: path to icon file
        """
        # open and read icon
        icon = self.readImage(icon_path)
        
        try:
            self._cursor.execute("UPDATE Icons SET name = :name, icon = :icon WHERE id = :id;",
                                {"icon" : icon, "name" : name, "id" : i_id})
            self._connection.commit()
            
            logging.info("icons updated: %i, with ID: %i, new icon image: %s", self._cursor.rowcount, i_id, icon_path)
        except sqlite3.IntegrityError as e:
            logging.warning(e)
            
            self._connection.rollback()
        except sqlite3.Error as e:
            logging.exception(e)
            
            self._connection.rollback()
            raise e
            
    def deleteIcon(self, i_id):
        """
            Delete icon with ID.
            @param g_id: group ID
        """
        try:
            self._cursor.execute("DELETE FROM Icons WHERE id = :id;", {"id" : i_id})
            self._connection.commit()
            
            count = self._cursor.rowcount
            
            if (count > 0):
                logging.info("%i icon with id: %i deleted", count, i_id)
            else:
                logging.info("%i icon with id: %i found", count, i_id)
        except sqlite3.Error as e:
            logging.exception(e)
            
            self._connection.rollback()
            raise e
            
    def readImage(self, path):
        """
            Reads image and prepare it for SQLite db.
            
            @param path: path to image
            @return: BLOB type
        """
        img = None
        icon = None
        
        # open and read icon
        try:
            logging.debug("reading icon image from path: %s", path)
            img = open(AppSettings.decodePath(path), "rb")
            
            icon = img.read()
            icon = sqlite3.Binary(icon)
        except IOError as e:
            logging.exception(e)
            
            raise e
        finally:
            if img:
                img.close()
            return icon
        
    def createIconObj(self, dic):
        """
            Creates icon from dictionary returned from db.
            
            @param dic: icon returned from db
            
            @return: IconModel object
        """
        return IconModel(dic["id"], dic["name"], dic["icon"])