"""
Note that endpoints are subject to change and some functions may brake as a result
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/"


def put_video_template_data():
	video_path = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources"
	template_path = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Templates"

	video = video_path + "\\mmlevel1.mp4"
	template_1 = template_path + "\\MegaManMoving.png"
	template_2 = template_path + "\\MegaManJumping.png"
	requests.put(BASE_URL + "edit/", data={"data": "{{\"video\":\"{}\", \"templates\": \"[{}, {}]\"}}".format(video,
	                                                                                                        template_1,
	                                                                                                        template_2)})


def put_video():
	video_path = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources\\mmlevel1.mp4"
	requests.put(BASE_URL + "add/video/", data={"data": "{{\"video\":\"{}\"}}".format(video_path)})


def put_template():
	template_path_1 = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Templates"
	template_1 = template_path_1 + r"\\MegaManMoving.png"
	template_2 = template_path_1 + r"\\MegaManJumping.png"
	template_3 = template_path_1 + r"\\MegaManAttacking.png"
	template_1_char = "r"
	template_2_char = "j"
	template_3_char= "a"
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


def edit_video(): requests.get(BASE_URL + "edit/")


if __name__ == "__main__":
	put_video()
	put_template()
	edit_video()
