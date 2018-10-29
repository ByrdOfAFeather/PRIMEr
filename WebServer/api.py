from flask import Flask, request
from flask_restful import Resource, Api
from database import DATABASE_PATH
from SideScrollers.VideoProcessing.TemplateScanners import ThreadedVideoScan
from SideScrollers.VideoProcessing.Template import Template
from SideScrollers.VideoProcessing.VideoEditors import VideoEditor
import sqlite3 as sql
import json


primer_server = Flask(__name__)
primer_server.config["DEBUG"] = True
primer_api = Api(primer_server)
template_dictionary = {}


def parse_list(parsable):
	parsable = parsable.replace("[", "").replace("]", "").split(",")
	return parsable


def edit_video():
	db = sql.connect(DATABASE_PATH)
	cursor = db.cursor()
	cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
	current_video = cursor.fetchall()[0][0]
	cursor.execute("""SELECT VIDEOPATH from VIDEOPATHS where VIDEOID = (?)""", (current_video,))
	video = cursor.fetchall()[0][0]

	cursor.execute("""SELECT * from TEMPLATEPATHS WHERE VIDEOID = (?)""", (current_video,))
	templates = cursor.fetchall()

	scanners = []
	for template in templates:
		current_template_id = template[1]
		current_template = Template(current_template_id, DATABASE_PATH)
		print(video)
		scanner = ThreadedVideoScan([current_template], video)
		scanners.append(scanner)
		scanner.start()

	[i.join() for i in scanners]
	print([j.output for j in scanners])
	final_output = []
	for scans in scanners: final_output.extend(scans.output)
	final_output.sort(key=lambda x: x.strip("j").strip("r"))
	tester = VideoEditor(video, final_output)
	tester.edit()
	print("Done!")


class EditVideo(Resource):
	def __init__(self):
		Resource.__init__(self)

	@staticmethod
	def get():
		edit_video()
		return {"STATUS": "SUCCESS"}


class AddEndPoint(Resource):
	def __int__(self):
		Resource.__init__(self)

	@staticmethod
	def put():
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data)
		return {"added_data": dict_data}


class VideoEndPoint(Resource):
	def __int__(self):
		Resource.__init__(self)

	@staticmethod
	def add_video(data_to_add):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""INSERT INTO VIDEOPATHS (VIDEOPATH) VALUES (?)""",
		               (data_to_add["video"],))
		db.commit()
		db.close()

	def put(self):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data)
		self.add_video(dict_data)
		return {"added_data": dict_data}


class TemplateEndPoint(Resource):
	def __init__(self):
		Resource.__init__(self)

	@staticmethod
	def add_template(data_to_add):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
		last_id = cursor.fetchall()[0][0]

		templates = parse_list(data_to_add["templates"])
		chars = parse_list(data_to_add["ordered_chars"])
		for template, char in zip(templates, chars):
			cursor.execute("""INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID, DESCRIPTOR) VALUES (?, ?, ?)""",
			               (template, last_id, char))
		db.commit()
		db.close()

	def put(self):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data)
		self.add_template(dict_data)


primer_api.add_resource(AddEndPoint, "/add/")
primer_api.add_resource(VideoEndPoint, "/add/video/")
primer_api.add_resource(TemplateEndPoint, "/add/template/")
primer_api.add_resource(EditVideo, "/edit/")


def run(): primer_server.run(port="5002")


if __name__ == "__main__": primer_server.run()
