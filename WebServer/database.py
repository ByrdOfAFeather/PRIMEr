"""
IMPORTATNT NOTES :
WHEN PUT INTO PRODUCTION THE DATABASE WILL HAVE TO BE ENTIRELY REDESIGNED, SPECIFICALLY TO DO WITH INDEXING BY ID
"""

import sqlite3 as sql
import os

DATABASE_NAME = "pathDB.db"
DATABASE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/" + DATABASE_NAME
print(DATABASE_PATH)

db = sql.connect(DATABASE_PATH)
cursor = db.cursor()
cursor.execute("""CREATE TABLE VIDEOPATHS(
					  VIDEOPATH TEXT,
					  VIDEOID INTEGER PRIMARY KEY  
					  ); 
               """)

cursor.execute("""
				  CREATE TABLE TEMPLATEPATHS(
				      TEMPLATEPATH TEXT,
				      TEMPLATEID INTEGER PRIMARY KEY ,
				      VIDEOID INT,
				      DESCRIPTOR TEXT
				      );
			   """)
