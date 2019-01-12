from flask import Flask, request
from flask_restful import Resource, Api
from database import DATABASE_PATH
from SideScrollers.VideoProcessing.TemplateScanners import ThreadedVideoScan
from SideScrollers.VideoProcessing.Template import Template
from SideScrollers.VideoProcessing.VideoEditors import VideoEditor
import sqlite3 as sql
import json
import urllib
import base64
# from flask_cors import CORS
#
# app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})



primer_server = Flask(__name__)
primer_server.config["DEBUG"] = True
primer_api = Api(primer_server)
template_dictionary = {}


@primer_server.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
	return response


def parse_list(parsable):
	parsable = parsable.replace("[", "").replace("]", "").split(",")
	return parsable


class EditVideo(Resource):
	@staticmethod
	def edit_video(video_id, yt_id):
		db = sql.connect(DATABASE_PATH)
		cursor = db.cursor()
		cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
		current_video = cursor.fetchall()[0][0]
		cursor.execute("""SELECT VIDEOPATH from VIDEOPATHS where VIDEOID = (?)""", (current_video,))
		video = cursor.fetchall()[0][0]

		cursor.execute("""SELECT * from TEMPLATEPATHS WHERE VIDEOID = (?)""", (current_video,))
		templates = cursor.fetchall()
		print(templates)

		scanners = []
		modeled_templates = []
		print(f"THIS IS TEMPLATES {templates}")

		for template in templates:
			current_template_id = template[1]

			current_template = Template(current_template_id, DATABASE_PATH)
			modeled_templates.append(current_template)

			scanner = ThreadedVideoScan([current_template], video)
			scanners.append(scanner)

			scanner.start()

		[i.join() for i in scanners]

		final_output = []
		for scans in scanners: final_output.extend(scans.output)
		final_output.sort(key=lambda x: x.time)

		tester = VideoEditor(video, final_output, yt_id)
		editor_result = tester.edit()
		output_json = str(editor_result).replace("'", '"')
		data = urllib.parse.urlencode([('gp', output_json)])
		with urllib.request.urlopen("https://tarheelgameplay.org/play", data=data.encode('utf-8')) as fp:
			result = fp.read()
		return result

	def __init__(self):
		Resource.__init__(self)

	def put(self):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data.replace(r'\x3E', '\x3E'))
		link = self.edit_video(dict_data["video_id"], dict_data["yt_id"])
		return {"LINK": str(link)}


class AddVideoToEdit(Resource):
	def __init__(self):
		Resource.__init__(self)

	@staticmethod
	def add_template(data_to_add):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
		last_id = cursor.fetchall()[0][0]
		print(data_to_add["templates"])
		templates = parse_list(data_to_add["templates"])
		chars = parse_list(data_to_add["ordered_chars"])
		for template, char in zip(templates, chars):
			cursor.execute("""INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID, DESCRIPTOR) VALUES (?, ?, ?)""",
			               (template, last_id, char))
		db.commit()
		db.close()

	@staticmethod
	def add_video(data_to_add):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""INSERT INTO VIDEOPATHS (VIDEOPATH) VALUES (?)""",
		               (data_to_add["video"],))
		db.commit()
		db.close()

	@staticmethod
	def current_video_id():
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
		last_id = cursor.fetchall()[0][0]
		cursor.close()
		return last_id

	def put(self):
		print(request)
		raw_data = request.form["data"]
		print(raw_data)
		dict_data = json.loads(raw_data.replace(r'\x3E', '\x3E'))
		self.add_video(dict_data)
		self.add_template(dict_data)
		video_id = self.current_video_id()
		return {"VIDEO ID": video_id}


class TestEndPoint(Resource):
	def __init__(self):
		Resource.__init__(self)

	def put(self):
		print("I got here")
		print(request)
		print(request.form)
		print(list(request.form.keys()))
		print(list(request.form.values()))
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data.replace(r'\x3E', '\x3E'))
		print(dict_data)
		for index, key in enumerate(dict_data["templates"]):
			for index2, templates in enumerate(dict_data["templates"][key]):
				with open(f"testkey{index}template{index2}.png", 'wb') as f:
					f.write(base64.b64decode(templates))
		return {"TEMPLATES ADDED"}


primer_api.add_resource(AddVideoToEdit, "/api/add/")
primer_api.add_resource(EditVideo, "/api/edit/")
primer_api.add_resource(TestEndPoint, "/api/test/")


def run():
	primer_server.run(port=5001)


if __name__ == "__main__": run()
