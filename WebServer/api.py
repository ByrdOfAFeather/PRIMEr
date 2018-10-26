import sqlite3 as sql
import json
from flask import Flask, request
from flask_restful import Resource, Api


primer_server = Flask(__name__)
primer_api = Api(primer_server)
template_dictionary = {}


def parse_list(parsable):
	parsable = parsable.replace("[", "").replace("]", "").split(",")
	return parsable


def add_items(data_to_add):
	db = sql.connect("pathDB.db")
	cursor = db.cursor()
	cursor.execute("""INSERT INTO VIDEOPATHS (VIDEOPATH) VALUES (?)""",
	               (data_to_add["video"], ))

	cursor.execute("""SELECT last_insert_rowid()""")
	last_id = cursor.fetchall()[0][0]

	templates = parse_list(data_to_add["templates"])
	for template in templates:
		cursor.execute("""INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID) VALUES (?, ?)""",
	                  (template, last_id))
	db.commit()
	db.close()


def edit_video(video_id):
	# TODO: Load video here
	# TODO: Load Templates here
	video = None
	templates = []
	scanners = []
	for i in templates:
		scanner = ThreadedVideoScan([i], video)
		scanners.append(scanner)


class EditEndPoint(Resource):
	def __int__(self):
		Resource.__init__(self)

	@staticmethod
	def get():
		pass

	@staticmethod
	def put(video_id):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data)
		add_items(dict_data)
		return {"added_data": dict_data}


class TemplateEndPoint(Resource):
	def __init__(self):
		Resource.__init__()

	@staticmethod
	def get():
		pass

	@staticmethod
	def put(video_id, id):
		pass


primer_api.add_resource(EditEndPoint, "/edit/<video_id>")
primer_api.add_resource(TemplateEndPoint, '/add-template/<video_id>/<id>')

def run():
	primer_server.run(port="5002")


if __name__ == "__main__": run()