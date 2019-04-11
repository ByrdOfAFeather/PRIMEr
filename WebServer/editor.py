import sys
sys.path.append("..")
import os
import json
import urllib.request
import urllib.parse
import shutil
import datetime
import cv2
from database import DATABASE_PATH
# from templatescanners import ThreadedVideoScan
from templatescannersbeta import ThreadedVideoScan
from VideoProcessing.VideoEditors import VanillaEditor, ConditionalEditor
from threading import Thread


# def string_to_timedelta(org_string):
# 	try:
# 		return_value = datetime.datetime.strptime(org_string, "%H:%M:%S.%f")
# 	except ValueError:
# 		return_value = datetime.datetime.strptime(org_string, "%H:%M:%S")
# 	return_value = datetime.timedelta(hours=return_value.hour,
# 	                               minutes=return_value.minute,
# 	                               seconds=return_value.second,
# 	                               microseconds=return_value.microsecond)
# 	return return_value
#
#
# def edit_video(timestamps, yt_id, video_editor_class, specials=None):
# 	if video_editor_class == ConditionalEditor:
# 		assert specials is not None, "GOT NO SPECIALS BUT GOT CONDITIONAL EDITOR, BREAKING"
# 		editor = video_editor_class(timestamps, yt_id, specials)
# 	else:
# 		editor = video_editor_class(timestamps, yt_id)
#
# 	editor_result = editor.edit()
# 	output_json = str(editor_result).replace("'", '"')
#
# 	print(f"FINAL OUTPUT JSON: {output_json}")
#
# 	data = urllib.parse.urlencode([('gp', output_json)])
# 	with urllib.request.urlopen("https://tarheelgameplay.org/play", data=data.encode('utf-8')) as fp:
# 		result = fp.read()
# 	return result
#
#
# # Function that is responsible for tying templates to a video and then sending them off to edit
# def scan_video(yt_id, video_editor_class, specials=None):
#
# 	for descriptor, template_id, template_path in unique_descriptors:
# 		try:
# 			current_templates[descriptor].append(template_path)
# 		except KeyError:
# 			current_templates[descriptor] = [template_path]
# 	print(video)
# 	print(current_templates)
#
# 	scanner = ThreadedVideoScan()
# 	final_output = scanner.run(current_templates, video)
# 	final_output.sort(key=lambda x: x.time)
#
# 	return edit_video(final_output, yt_id, video_editor_class, specials)
#
#
# def add_video(video_id):
# 	db = sql.connect("pathDB.db")
# 	cursor = db.cursor()
# 	cursor.execute("""INSERT INTO VIDEOPATHS (VIDEOPATH) VALUES (?)""",
# 	               (f"VideoFiles/{video_id}.mp4",))
# 	db.commit()
# 	db.close()
#
#
# def add_templates(path, descriptor, db_video_id):
# 	db = sql.connect("pathDB.db")
# 	cursor = db.cursor()
# 	cursor.execute("""SELECT VIDEOID FROM VIDEOPATHS WHERE VIDEOID = (?)""", (db_video_id, ))
# 	video_id = cursor.fetchall()[0][0]
# 	cursor.execute("""INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID, DESCRIPTOR) VALUES (?, ?, ?)""",
# 	               (path, video_id, descriptor))
# 	db.commit()
# 	db.close()
#
#
# def export_templates(video_id, video_list, db_video_id):
# 	if not os.path.exists(f"TemplateFiles/{video_id}"): os.makedirs(f"TemplateFiles/{video_id}")
# 	for template_type in video_list:
# 		safe_name = template_type.replace(" ", "").replace("<", "").replace(">", "").replace("\"", "")\
# 			.replace("/", "").replace("\\", "").replace("|", "").replace("?", "").replace("*", "")
# 		template_storage_path = f"TemplateFiles/{video_id}/{safe_name}"
#
# 		loaded_video = cv2.VideoCapture(f"VideoFiles/{video_id}.mp4")
#
# 		for index, template_code in enumerate(video_list[template_type]):
# 			frame_rate = loaded_video.get(cv2.CAP_PROP_FPS)
# 			template_code["currentFrame"] = template_code["currentFrame"] * frame_rate
# 			loaded_video.set(cv2.CAP_PROP_POS_FRAMES, template_code["currentFrame"])
# 			is_image, frame = loaded_video.read()
# 			template = frame[round(template_code["realRectY"]):
# 			                 round(template_code["realRectY"] + template_code["rectangleHeight"]),
# 			                 round(template_code["realRectX"]):
# 			                 round(template_code["realRectX"] + template_code["rectangleWidth"])]
# 			indiv_template_path = template_storage_path + f"/{index}.png"
# 			cv2.imwrite(indiv_template_path, template)
#
#
# def put(videoID, template_data):
#
# 	video_editor = VanillaEditor
#
# 	if input_data["conditionals"]:
# 		print(input_data["conditionals"])
# 		print("PUNISHMENT MODULE COMPONENTS DETECTED: EDITING WITH CONDITIONAL VIDEO EDITOR")
# 		video_editor = ConditionalEditor
#
# 	export_templates(input_data["videoID"], input_data["templates"], input_data["dbVideoID"])
#
# 	class EditThread(Thread):
# 		def __init__(self):
# 			Thread.__init__(self)
# 			self.output = None
#
# 		def run(self):
# 			value = scan_video(input_data["videoID"], video_editor, input_data["conditionals"])
# 			value = value.decode()[8:].replace("\"", "").replace("{", "").replace("}", "")
# 			self.output = f'https://tarheelgameplay.org/play/?key={value}'
#
# 	editor = EditThread()
# 	editor.start()
# 	editor.join()
# 	return editor.output


videoID = sys.argv[1]
template_data = sys.argv[2]
print(template_data)
# url = put(videoID, template_data)
# print(url)
# print("DONE")
