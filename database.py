import sqlite3 as sql
import os

DATABASE_NAME = "pathDB.db"
DATABASE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/" + DATABASE_NAME


def run():
	db = sql.connect(DATABASE_PATH)
	cursor = db.cursor()
	cursor.execute("""
		CREATE TABLE VIDEOPATHS(
			VIDEOPATH TEXT,
			VIDEOID INTEGER PRIMARY KEY
			);
	""")

	cursor.execute("""
		CREATE TABLE TEMPLATEPATHS(
			TEMPLATEPATH TEXT,
			TEMPLATEID INTEGER PRIMARY KEY,
			VIDEOID INT,
			DESCRIPTOR TEXT,
			DATA TEXT 
		);
	""")

	cursor.execute("""
		CREATE TABLE QUEUE (
			QUEUEID INTEGER PRIMARY KEY,
			VIDEOID INTEGER
		);
	""")

	cursor.execute("""
		CREATE TABLE RESULTS (
			RESULTID INTEGER PRIMARY KEY, 
			LINK INTEGER
		);
	""")


if __name__ == "__main__": run()
