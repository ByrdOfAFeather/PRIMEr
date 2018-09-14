"""A general class for using a template to scan an image
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/1/2018
"""
import cv2
import matplotlib.pyplot as plt


class TemplateScanner:
	def __init__(self, templates):
		self.template_list = templates
		self.cur_best_template = None
		self.cur_results = None
		self.template_list = self.build_image_list("Templates", *self.template_list)

	def plot_template_match(self, image, template_results, title="Template Matching result", output_title="TEST"):
		"""Plots the image with the rectangle overlayed on top of it. (Inspired from: https://docs.opencv.org/3.4.3/d4/dc6/tutorial_py_template_matching.html)
		:param image: A cv2.imread() variable of the original image
		:param template_results: The results of running the template inside of cv2's matching method
		:param title: The desired title of the graph
		:param output_title: the template for outputting files with different names
		:return:
		"""
		h, w = self.cur_best_template.shape[:-1]
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_results)
		print("THIS IS MAX {}".format(max_val))
		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		cv2.rectangle(image, top_left, bottom_right, 255, 10)
		plt.title(title)
		plt.xticks([]), plt.yticks([])
		plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
		# plt.show()
		plt.savefig(f"Output/{output_title}.png")

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
			image_color = cv2.imread(f"{directory}/{name}")
			image_color_flipped = cv2.flip(image_color, 1)
			filter_array.append(image_color)
			filter_array.append(image_color_flipped)
		return filter_array

	def scan(self, image_list, threshold=0):
		"""Scans through the images passed to the original class and appends true if they should be printed and false otherwise
		:param image_list: List of images to be scanned
		:return: boolean list of true or false
		"""
		# Loops through all the mario jumping images
		images_to_print = []
		for image in image_list:
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
			self.cur_results = filter_maxs[cur_max_index]
			self.cur_best_template = self.template_list[cur_max_index]

			# (Working Garfield: 29575692, Actual working mario: 100588760)
			if filter_maxs[cur_max_index][1] < threshold:  # 143160288:  # 73815312: # 99587656:
				images_to_print.append(False)

			else:
				images_to_print.append(True)
		return images_to_print


class VideoScanner(TemplateScanner):
	def __init__(self, templates):
		TemplateScanner.__init__(self, templates)

	def get_average_match(self, video):
		frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

		list_of_maxes = []

		no_completed = 0
		i = 0

		# Minus the frame count by 10 to give a little buffer room so that the video doesnt run out of frames)
		while i < (frame_count - 10):
			video.set(1, i)
			_, frame = video.read()
			self.scan([frame])
			list_of_maxes.append(self.cur_results[1])

			i += 10
			no_completed += 1

		video.set(1, 0)
		average = sum(list_of_maxes) / len(list_of_maxes)
		threshold = [i for i in list_of_maxes if i > average][5]
		return threshold

	def scan_video(self, video, output_generic="LevelX_Frame"):
		video = cv2.VideoCapture(video)
		threshold = self.get_average_match(video)
		print(threshold)

		index = 0

		# Slider as to not get all frames of a single jump, instead only getting as close to the first one as possible
		slider = [0, 0, 0, 0, 0, 0]

		# Slider to keep track of the image frames as corresponding to the original slider
		image_slider = [0, 0, 0, 0, 0, 0]

		# Defaults the skip index to -1 so as to not create an infinite loop
		skip_index = -1

		while True:

			# If the skip index is greater than 0, reset the sliders and increase the skip index
			if 0 <= skip_index <= len(slider):

				# slides the video forward
				_, _ = video.read()

				# increase the index
				skip_index += 1
				index += 1

				slider = [0, 0, 0, 0, 0, 0, 0]
				image_slider = [0, 0, 0, 0, 0, 0, 0]

				if cv2.waitKey(1) & 0xFF == ord('q'): break
				continue

			# Read the current frame into greyscale
			_, frame = video.read()

			# Add new items to the image slider
			image_slider.pop(0)
			image_slider.append(frame)

			# Get the export of the scanner
			export = self.scan([frame], threshold=threshold)

			# Slide the slider and get the average
			slider.pop(0)
			slider.append(1 if export[0] else 0)
			average = sum(slider) / len(slider)

			# If the average value is greater than the threshold it's pretty likely there is a jump happening
			if average >= .5:
				cv2.imshow("frame", frame)

				# Get the index of the first positive jump frame and plot it
				index_of_positive = [index for index, value in enumerate(slider) if value == 1][0]
				self.scan([image_slider[index_of_positive]])
				self.plot_template_match(image_slider[index_of_positive], self.cur_results[0],
				                         output_title=f"{output_generic}{index}")

				skip_index = 0

			# Taken from cv2 guide to videos:
			if cv2.waitKey(1) & 0xFF == ord('q'): break

			index += 1


# 15516919.0
level1 = VideoScanner(templates=["EdwardJumping.png"])  # "MarioFireJump.png"])
level1.scan_video("Sources/FMAlvl1.mp4", output_generic="FMAGameLevel1Frame")
