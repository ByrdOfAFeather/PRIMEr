from TemplateScanner import TemplateScanner
import cv2
import matplotlib.pyplot as plt
from datetime import datetime


def match_template(image, template, filter_process):
	"""Returns the evaluation of a template's similarity to an image
	:param image: A cv2.imread() loaded image
	:param template: Another cv2.imread() image that is scanned for in image
	:param filter_process: The type of cv2 filter to use (see: https://docs.opencv.org/3.4.3/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
	:return: None
	"""
	filter_process = eval(filter_process)
	return cv2.matchTemplate(image, template, filter_process)


def build_filter(*image_names):
	"""Builds an array of filters based on the passed file names
	:param image_names: File names of filters *note: have to be stored in the /Templates/ directory
	:return: None
	"""
	filter_array = []
	for name in image_names:
		filter_array.append(cv2.imread(f"Templates/{name}", 0))
	return filter_array


def plot_template_match(image, template, template_results, title="Template Matching result"):
	"""Plots the image with the rectangle put on top of it. (Inspired from: https://docs.opencv.org/3.4.3/d4/dc6/tutorial_py_template_matching.html)
	:param image: A cv2.imread() variable of the original image
	:param template: A cv2.imread() variable of the template
	:param template_results: The results of running the template inside of cv2's matching method
	:param title: The desired title of the graph
	:return:
	"""
	w, h = template.shape[::-1]
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_results)

	top_left = max_loc
	bottom_right = (top_left[0] + w, top_left[1] + h)

	cv2.rectangle(image, top_left, bottom_right, 255, 10)
	plt.title(title)
	plt.xticks([]), plt.yticks([])
	plt.imshow(image, cmap="gray")
	plt.show()


def main(): pass


if __name__ == "__main__": main()
