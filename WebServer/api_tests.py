"""
Note that endpoints are subject to change and some functions may brake as a result
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5001/api/"

video_path = r"P:\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources"
template_path = r"P:\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Templates"

# video_path = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Sources"
# template_path = r"C:\\Users\\Matthew Byrd\\OneDrive\\ByrdOfAFeather\\Python\\PRIMEr\\SideScrollers\\VideoProcessing\\Templates"


def put_video_template_data():
	template_1 = template_path + r"\\TestMMJumping.png"
	template_2 = template_path + r"\\TestMegaManMoving.png"
	template_3 = template_path + r"\\TestMegaManAttacking.png"
	vid = video_path + r"\\mmlong.mp4"

	template_1_char = "Jumping"
	template_2_char = "Run"
	template_3_char = "Attack"

	put_r = requests.put(BASE_URL + "add/", data={"data": "{{\"templates\": \"[{}, {}, {}]\", "
	                                                      "\"ordered_chars\": \"[{}, {}, {}]\","
	                                                      "\"video\": \"{}\"}}".format(template_1,
	                                                                                   template_2,
	                                                                                   template_3,
	                                                                                   template_1_char,
	                                                                                   template_2_char,
	                                                                                   template_3_char,
	                                                                                   vid
	                                                                                   )
	                                              }
	                     )
	return put_r.json()["VIDEO ID"]


def edit_video(most_recent_id):
	edit_r = requests.put(BASE_URL + "edit/", data={"data": "{{\"video_id\": \"{}\", "
	                                                        "\"yt_id\": \"{}\"}}".format(most_recent_id,
	                                                                                     "NP697v8WtkU")})
	print(edit_r.content)


if __name__ == "__main__":
	print("PRINTING")
	video_id = put_video_template_data()
	print("DONE PRINTING")
	edit_video(video_id)
