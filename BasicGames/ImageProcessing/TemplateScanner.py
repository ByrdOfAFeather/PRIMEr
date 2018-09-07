"""A general class for using a template to scan an image
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/1/2018
"""
import cv2
import matplotlib.pyplot as plt


class TemplateScanner:
	def __init__(self, templates, images, image_dir):
		self.template_list = templates
		self.image_list = images
		self.cur_best_template = None
		self.cur_results = None

		self.template_list = self.build_image_list("Templates", *self.template_list)
		# self.image_list = self.build_image_list(image_dir, *self.image_list)

	def plot_template_match(self, image, template_results, title="Template Matching result", index=""):
		"""Plots the image with the rectangle overlayed on top of it. (Inspired from: https://docs.opencv.org/3.4.3/d4/dc6/tutorial_py_template_matching.html)
		:param image: A cv2.imread() variable of the original image
		:param template: A cv2.imread() variable of the template
		:param template_results: The results of running the template inside of cv2's matching method
		:param title: The desired title of the graph
		:param index: Keeps track of external index for the title of graphs
		:return:
		"""
		w, h = self.cur_best_template.shape[::-1]
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_results)

		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		cv2.rectangle(image, top_left, bottom_right, 255, 10)
		plt.title(title)
		plt.xticks([]), plt.yticks([])
		plt.imshow(image, cmap="gray")
		# plt.show()
		plt.savefig(f"OutPut/Test{index}.png")

	@staticmethod
	def match_template(image, template, filter_process):
		"""Returns the evaluation of a template's similarity to an image
		:param image: A cv2.imread() loaded image
		:param template: Another cv2.imread() image that is scanned for in image
		:param filter_process: The type of cv2 filter to use (see: https://docs.opencv.org/3.4.3/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
		:return: None
		"""
		filter_process = eval(filter_process)
		return cv2.matchTemplate(image, template, filter_process)

	@staticmethod
	def build_image_list(directory, *image_names):
		"""Builds an array of filters based on the passed file names
		:param directory: The storage location of files
		:param image_names: File names of filters *note: have to be stored in the /Templates/ directory
		:return: None
		"""
		filter_array = []
		for name in image_names:
			filter_array.append(cv2.imread(f"{directory}/{name}", 0))
		return filter_array

	def scan(self):
		"""Scans through the images passed to the original class and appends true if they should be printed and false otherwise
		:return: boolean list of true or false
		"""
		# Loops through all the mario jumping images
		images_to_print = []
		for image in self.image_list:
			filter_maxs = {}
			cur_max_index = 0

			# Loops through all the filter images and finds the most similar one to the current photo
			for index, filters in enumerate(self.template_list):
				results = self.match_template(image, filters, "cv2.TM_CCOEFF")
				_, max_val, _, _ = cv2.minMaxLoc(results)
				if index > 0:
					if max_val < filter_maxs[index - 1][1]:
						pass
					else:
						cur_max_index = index
				else:
					cur_max_index = index
				filter_maxs[index] = (results, max_val)
			self.cur_results, _ = filter_maxs[cur_max_index]
			self.cur_best_template = self.template_list[cur_max_index]

			if filter_maxs[cur_max_index][1] < 8984554:   # 175697584.0:
				images_to_print.append(False)

			images_to_print.append(True)
		return images_to_print

