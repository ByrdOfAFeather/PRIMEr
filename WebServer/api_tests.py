"""
Note that endpoints are subject to change and some functions may brake as a result
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/"

video_path = r"C:\\Users\\matth\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources"
template_path = r"C:\\Users\\matth\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Templates"


def put_video_template_data():

	video = video_path + "\\mmlevel1.mp4"
	template_1 = template_path + "\\MegaManMoving.png"
	template_2 = template_path + "\\MegaManJumping.png"
	requests.put(BASE_URL + "edit/", data={"data": "{{\"video\":\"{}\", \"templates\": \"[{}, {}]\"}}".format(video,
	                                                                                                        template_1,
	                                                                                                        template_2)})


def put_video():
	video_path = r"C:\\Users\\matth\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources\\mmlevel3.mp4"
	requests.put(BASE_URL + "add/video/", data={"data": "{{\"video\":\"{}\"}}".format(video_path)})


def put_template():
	template_1 = template_path + r"\\MegaManMoving.png"
	template_2 = template_path + r"\\MegaManJumping.png"
	template_3 = template_path + r"\\MegaManAttacking.png"
	template_1_char = "Run"
	template_2_char = "Jump"
	template_3_char = "Attack"
	requests.put(BASE_URL + "add/template/", data={"data": "{{\"templates\": \"[{}, {}, {}]\", "
	                                                       "\"ordered_chars\": \"[{}, {}, {}]\"}}".format(template_1,
	                                                                                                      template_2,
	                                                                                                      template_3,
	                                                                                                      template_1_char,
	                                                                                                      template_2_char,
                                                                                                          template_3_char,
	                                                                                                      )
	                                               }
	             )


def edit_video():
	edit_r = requests.get(BASE_URL + "edit/")
	print(edit_r.content)


if __name__ == "__main__":
	put_video()
	put_template()
	edit_video()
