import sqlite3 as sql

db = sql.connect("pathDB.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE EDITDATA(
					  VIDEOPATH TEXT, 
					  TEMPLATESPATH TEXT); """)
db.commit()
db.close()