from flask import Flask, request
from flask_restful import Resource, Api
from database import DATABASE_PATH
from SideScrollers.VideoProcessing.TemplateScanners import ThreadedVideoScan
from SideScrollers.VideoProcessing.Template import Template
from SideScrollers.VideoProcessing.VideoEditors import VideoEditor
from threading import Thread
import os
import sqlite3 as sql
import json
import urllib
import base64


# Set up the server and api
primer_server = Flask(__name__)
primer_server.config["DEBUG"] = True
primer_api = Api(primer_server)
template_dictionary = {}


# Allows for requests to be made from domains not hosted on the server
@primer_server.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
	return response


# Generic function to parse lists into a sql readable format
def parse_list(parsable):
	parsable = parsable.replace("[", "").replace("]", "").split(",")
	return parsable


# Function that is responsible for tying templates to a video and then sending them off to edit
def edit_video(yt_id):
	db = sql.connect(DATABASE_PATH)
	cursor = db.cursor()

	# TODO: Find a more robust way of storing unique video IDs
	# Gets the video ID, in this case, the most recent video added to the database is assumed to be the correct one
	cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
	current_video = cursor.fetchall()[0][0]

	# Gets the video path associated with the most recent ID
	cursor.execute("""SELECT VIDEOPATH from VIDEOPATHS where VIDEOID = (?)""", (current_video,))
	video = cursor.fetchall()[0][0]

	# Gets a list of unique descriptors for the templates associated with the video
	cursor.execute("""SELECT DISTINCT DESCRIPTOR from TEMPLATEPATHS WHERE VIDEOID = (?)""", (current_video,))
	descriptors = cursor.fetchall()
	print(f"THESE ARE THE DESCRIPTORS I AM WORKING WITH {descriptors}")

	scanners = []
	for descriptor in descriptors:
		# Gets all the templates associated with the current descriptor
		descriptor = descriptor[0]
		cursor.execute("""SELECT TEMPLATEID from TEMPLATEPATHS WHERE VIDEOID = (?) AND DESCRIPTOR = (?)""",
		               (current_video, descriptor))
		templates = cursor.fetchall()

		# Gets the template IDs for each template with the current descriptor and create objects for reference
		current_templates = []
		for template in templates:
			template_id = template[0]
			current_template = Template(template_id, DATABASE_PATH)
			current_templates.append(current_template)
			print(current_templates)

		scanner = ThreadedVideoScan(current_templates, video)
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


class StartEditEndPoint(Resource):
	def __init__(self):
		Resource.__init__(self)

	def edit(self):
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

	@staticmethod
	def add_video(video_id):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""INSERT INTO VIDEOPATHS (VIDEOPATH) VALUES (?)""",
		               (f"VideoFiles/{video_id}.mp4",))
		db.commit()
		db.close()

	@staticmethod
	def add_templates(path, descriptor):
		db = sql.connect("pathDB.db")
		cursor = db.cursor()
		cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
		video_id = cursor.fetchall()[0][0]
		cursor.execute("""INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID, DESCRIPTOR) VALUES (?, ?, ?)""",
		               (path, video_id, descriptor))
		db.commit()
		db.close()

	def export_videos(self, video_id, video_list):
		if not os.path.exists(f"TemplateFiles/{video_id}"): os.makedirs(f"TemplateFiles/{video_id}")
		for template_type in video_list:
			safe_name = template_type.replace(" ", "").replace("<", "").replace(">", "").replace("\"", "")\
				.replace("/", "").replace("\\", "").replace("|", "").replace("?", "").replace("*", "")
			template_storage_path = f"TemplateFiles/{video_id}/{safe_name}"
			os.makedirs(template_storage_path)
			for index, template_code in enumerate(video_list[template_type]):
				indiv_template_path = template_storage_path + f"/{index}.png"
				self.add_templates(indiv_template_path, safe_name)
				with open(indiv_template_path, 'wb') as f:
					f.write(base64.b64decode(template_code))

	def put(self):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data.replace(r'\x3E', '\x3E'))
		self.add_video(dict_data["videoID"])
		self.export_videos(dict_data["videoID"], dict_data["templates"])

		class EditThread(Thread):
			def __init__(self):
				Thread.__init__(self)

			def run(self):
				print(edit_video(dict_data["videoID"]))

		editor = EditThread()
		editor.start()
		return {"TEMPLATES": "ADDED"}


primer_api.add_resource(StartEditEndPoint, "/api/startedit/")


def run():
	primer_server.run(port=5001)


if __name__ == "__main__": run()
