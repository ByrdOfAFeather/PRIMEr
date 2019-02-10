from flask import Flask, request
from flask_restful import Resource, Api
from database import DATABASE_PATH
from TemplateScanners import ThreadedVideoScan
from VideoProcessing.Template import Template
from VideoProcessing.VideoEditors import VanillaEditor, ConditionalEditor
from VideoProcessing.Timestamp import Timestamp
from threading import Thread
import os
import sqlite3 as sql
import json
import urllib
import base64
import shutil
import datetime


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


def string_to_timedelta(org_string):
	try:
		return_value = datetime.datetime.strptime(org_string, "%H:%M:%S.%f")
	except ValueError:
		return_value = datetime.datetime.strptime(org_string, "%H:%M:%S")
	return_value = datetime.timedelta(hours=return_value.hour,
	                               minutes=return_value.minute,
	                               seconds=return_value.second,
	                               microseconds=return_value.microsecond)
	return return_value


def edit_video(timestamps, yt_id, video_editor_class, specials=None):
	if video_editor_class == ConditionalEditor:
		assert specials is not None, "GOT NO SPECIALS BUT GOT CONDITIONAL EDITOR, BREAKING"
		editor = video_editor_class(timestamps, yt_id, specials)
	else:
		editor = video_editor_class(timestamps, yt_id)

	editor_result = editor.edit()
	output_json = str(editor_result).replace("'", '"')

	print(f"FINAL OUTPUT JSON: {output_json}")

	data = urllib.parse.urlencode([('gp', output_json)])
	with urllib.request.urlopen("https://tarheelgameplay.org/play", data=data.encode('utf-8')) as fp:
		result = fp.read()
	# result = "NOT CURRENTLY ADDING THIS VIDEO TO TARHEELHAMEPLAY"
	return result


# Function that is responsible for tying templates to a video and then sending them off to edit
def scan_video(yt_id, video_editor_class, specials=None):
	save_direct = f"TemplateFiles/{yt_id}/"

	# Development Tools
	if os.environ.get('DEV', '') and os.path.exists(f"{save_direct}/scanneroutput.txt"):
		with open(f"{save_direct}/scanneroutput.txt", "r") as f:
			saved_list = f.readline().replace("'", "").replace(" ", "").strip('[').strip(']').split(',')

		index = 0
		tupled_list = []
		while index < len(saved_list):
			current_item = saved_list[index].replace("'", "").replace("(", "").replace(")", "")
			next_item = saved_list[index + 1].replace("'", "").replace("(", "").replace(")", "")
			tupled_list.append((current_item, next_item))
			index += 2

		final_output = [Timestamp(times[0], string_to_timedelta(times[1])) for times in tupled_list]
		return edit_video(final_output, yt_id, video_editor_class, specials)

	db = sql.connect(DATABASE_PATH)
	cursor = db.cursor()

	# TODO: Find a more robust way of storing unique video IDs
	# Gets the video ID, in this case, the most recent video added to the database is assumed to be the correct one
	cursor.execute("""SELECT MAX(VIDEOID) from VIDEOPATHS""")
	results = cursor.fetchall()
	print(f"HEY THIS IS THAT TEST YOU WANT TO REMEMBER {results}")
	current_video = results[0][0]

	# Gets the video path associated with the most recent ID
	cursor.execute("""SELECT VIDEOPATH from VIDEOPATHS where VIDEOID = (?)""", (current_video,))
	video = cursor.fetchall()[0][0]

	# Gets a list of unique descriptors for the templates associated with the video
	# cursor.execute("""SELECT * FROM TEMPLATEPATHS GROUP BY DESCRIPTOR""")
	cursor.execute("""SELECT DISTINCT DESCRIPTOR, TEMPLATEID, TEMPLATEPATH from TEMPLATEPATHS WHERE VIDEOID = (?)""", (current_video,))
	unique_descriptors = cursor.fetchall()
	print(f"THIS IS THE RESULT FROM QUERY {unique_descriptors}")

	# Gets the template IDs for each template with the current descriptor and create objects for reference
	current_templates = {}

	for descriptor, template_id, template_path in unique_descriptors:
		try:
			current_templates[descriptor].append(template_path)
		except KeyError:
			current_templates[descriptor] = [template_path]
	print(video)
	print(current_templates)

	scanner = ThreadedVideoScan()
	final_output = scanner.run(current_templates, video, .7)
	final_output.sort(key=lambda x: x.time)

	# Development Tools
	if os.environ.get('DEV', ''):
		save_list = [(timestamps.marker, str(timestamps.time)) for timestamps in final_output]
		with open(f"{save_direct}/scanneroutput.txt", "w") as f:
			f.write(str(save_list))

	return edit_video(final_output, yt_id, video_editor_class, specials)


class StartEditEndPoint(Resource):
	def __init__(self):
		Resource.__init__(self)

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

			if os.path.exists(template_storage_path):
				shutil.rmtree(template_storage_path, ignore_errors=True)

			os.makedirs(template_storage_path)

			for index, template_code in enumerate(video_list[template_type]):
				indiv_template_path = template_storage_path + f"/{index}.png"
				self.add_templates(indiv_template_path, safe_name)
				with open(indiv_template_path, 'wb') as f:
					f.write(base64.b64decode(template_code))

	def put(self):
		raw_data = request.form["data"]
		dict_data = json.loads(raw_data.replace(r'\x3E', '\x3E'))
		video_editor = VanillaEditor
		if dict_data["conditionals"]:
			print(dict_data["conditionals"])
			print("PUNISHMENT MODULE COMPONENTS DETECTED: EDITING WITH CONDITIONAL VIDEO EDITOR")
			video_editor = ConditionalEditor
		self.add_video(dict_data["videoID"])
		self.export_videos(dict_data["videoID"], dict_data["templates"])

		class EditThread(Thread):
			def __init__(self):
				Thread.__init__(self)

			def run(self):
				value = scan_video(dict_data["videoID"], video_editor, dict_data["conditionals"])
				value = value.decode()[8:].replace("\"", "").replace("{", "").replace("}", "")
				print(
					f'https://tarheelgameplay.org/play/?key={value}'
				)

		editor = EditThread()
		editor.start()
		return {"TEMPLATES": "ADDED"}


primer_api.add_resource(StartEditEndPoint, "/api/startedit/")


def run():
	primer_server.run(port=5001)


if __name__ == "__main__": run()
