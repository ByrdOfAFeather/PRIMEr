import sys
sys.path.append("..")
import json
import urllib.request
import urllib.parse
import datetime
import cv2
import sqlite3 as sql
from database import DATABASE_PATH
# from templatescanners import ThreadedVideoScan
from templatescannersbeta import ThreadedVideoScan
from VideoProcessing.VideoEditors import VanillaEditor, ConditionalEditor
from threading import Thread


def parse_sql_data(video_id):
	reader = sql.connect("pathDB.db")
	cursor = reader.cursor()
	cursor.execute(
		"""SELECT DISTINCT DESCRIPTOR, TEMPLATEID, TEMPLATEPATH, DATA from TEMPLATEPATHS WHERE VIDEOID = (?)""",
		(video_id,)
	)

	data = cursor.fetchall()
	template_dict = {}
	for i, templates in enumerate(data):
		try:
			template_dict[templates[0]].append({"PATH": templates[2], "DATA": json.loads(templates[3])})
		except KeyError:
			template_dict[templates[0]] = [{"PATH": templates[2], "DATA": json.loads(templates[3])}]

	return template_dict


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
	return result


def scan_video(init_passable_dict, init_path, video_editor, specials=None):
	scanner = ThreadedVideoScan()
	final_output = scanner.run(init_passable_dict, init_path)
	final_output.sort(key=lambda x: x.time)

	yt_id = init_path.split("/")[1].replace(".mp4", "")
	return edit_video(final_output, yt_id, video_editor, specials)


def export_templates(init_template_dict):
	passable_dict = {}
	example = ""
	for template_type in list(init_template_dict.keys()):
		for template in init_template_dict[template_type]:
			example = template["PATH"]
			try:
				passable_dict[template_type].append(template["PATH"])
			except KeyError:
				passable_dict[template_type] = [template["PATH"]]

			vid_path = template["PATH"]
			vid_path = vid_path.split("/")
			loaded_video = cv2.VideoCapture(f"VideoFiles/{vid_path[1]}.mp4")

			frame_rate = loaded_video.get(cv2.CAP_PROP_FPS)
			template_code = template["DATA"]
			template_code["currentFrame"] = template_code["currentFrame"] * frame_rate
			loaded_video.set(cv2.CAP_PROP_POS_FRAMES, template_code["currentFrame"])
			is_image, frame = loaded_video.read()
			exportable_template = frame[round(template_code["realRectY"]):
			                            round(template_code["realRectY"] + template_code["rectangleHeight"]),
			                      round(template_code["realRectX"]):
			                      round(template_code["realRectX"] + template_code["rectangleWidth"])]
			cv2.imwrite(template["PATH"], exportable_template)
			cv2.imwrite(template["PATH"] + "flipped.png", cv2.flip(exportable_template, 1))

	temp_path = example.split("/")
	yt_id = temp_path[1]
	return passable_dict, f"VideoFiles/{yt_id}.mp4"


def start_edit(init_pass_dict, init_path):
	video_editor = VanillaEditor

	try:
		template_dict["Punishment"]
		print("PUNISHMENT MODULE COMPONENTS DETECTED: EDITING WITH CONDITIONAL VIDEO EDITOR")
		video_editor = ConditionalEditor

	except KeyError:
		print("NO CONDITIONALS")

	class EditThread(Thread):
		def __init__(self):
			Thread.__init__(self)
			self.output = None

		def run(self):
			value = scan_video(init_pass_dict, init_path, video_editor)
			value = value.decode()[8:].replace("\"", "").replace("{", "").replace("}", "")
			self.output = f'https://tarheelgameplay.org/play/?key={value}'

	editor = EditThread()
	editor.start()
	editor.join()
	return editor.output


videoID = sys.argv[1]
template_dict = parse_sql_data(videoID)
pass_dict, path = export_templates(template_dict)
url = start_edit(pass_dict, path)
print(url)
print("DONE")
