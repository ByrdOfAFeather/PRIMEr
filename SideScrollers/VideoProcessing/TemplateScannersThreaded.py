"""A general class for using a template to scan a image using multiple threads
Author: Matthew Byrd
Date created: 9/21/2018
Date last modified: 8/5/2018
"""
import datetime

import cv2
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread

RETURN_TIMESTAMPS = 0
RETURN_THRESHOLD = 1


class TemplateScanner:
	def __init__(self, templates):
		self.template_list = templates
		self.cur_best_template = None
		self.cur_results = None
		self.template_list = self._build_image_list("Templates", *self.template_list)

	def plot_template_match(self, image, template_results, title="Template Matching result", output_title="TEST"):
		"""Plots the image with the rectangle put on top of it. (Inspired from: https://docs.opencv.org/3.4.3/d4/dc6/tutorial_py_template_matching.html)
		:param image: A cv2.imread() variable of the original image
		:param template_results: The results of running the template inside of cv2's matching method
		:param title: The desired title of the graph
		:param output_title: the template for outputting files with different names
		:return: None
		"""
		h, w = self.cur_best_template.shape[:-1]
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_results)
		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		cv2.rectangle(image, top_left, bottom_right, 255, 10)
		plt.title(title)
		plt.xticks([]), plt.yticks([])
		plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
		plt.savefig(f"Output/{output_title}.png")

	@staticmethod
	def _match_template(image, template, filter_process):
		"""Returns the evaluation of a template's similarity to an image
		:param image: A cv2.imread() loaded image
		:param template: Another cv2.imread() image that is scanned for in image
		:param filter_process: The type of cv2 equation to use (see: https://docs.opencv.org/3.4.3/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
		:return: None
		"""
		filter_process = eval(filter_process)
		return cv2.matchTemplate(image, template, filter_process)

	@staticmethod
	def _build_image_list(directory, *image_names):
		"""Builds an array of templates based on the passed file names
		:param directory: The storage location of files
		:param image_names: File names of templates *note: have to be stored in the /Templates/ directory
		:return: None
		"""
		template_list = []
		for name in image_names:
			image_color = cv2.imread(f"{directory}/{name}")
			image_color_flipped = cv2.flip(image_color, 1)
			template_list.append(image_color)
			template_list.append(image_color_flipped)
		return template_list

	def _get_best_match(self, image):
		"""Gets the best match given a list of templates
		:param image: an cv2 image type
		:return:
		"""
		template_maxes = {}
		cur_max_index = 0
		for index, templates in enumerate(self.template_list):
			# Gets the results from cv2's image match on a single template for a single image
			results = self._match_template(image, templates, "cv2.TM_CCOEFF")

			# Gets the highest template match value
			_, max_val, _, _ = cv2.minMaxLoc(results)

			# If this isn't the first index
			if index > 0:
				# If the current maximum template match is smaller than the maximum template match from the previous
				if max_val < template_maxes[index - 1][1]:
					# Ignore the value
					pass
				else:
					# If we have a larger maximum value, we want to use that template instead
					cur_max_index = index
			else:
				cur_max_index = index

			template_maxes[index] = (results, max_val)

		return cur_max_index, template_maxes

	def scan(self, image_list, threshold=0):
		"""Scans through the images passed to the original class and builds a list of T/F for if the template was found
		:param image_list: List of images to be scanned
		:param threshold: The numeric value at which a template match is to be considered a negative
		:return: boolean list of true or false describing when an image was found
		"""
		# Loops through all the mario jumping images
		images_with_template = []
		for image in image_list:
			template_maxes = {}
			cur_max_index = 0

			# Loops through all the filter images and finds the most similar one to the current photo [Multi template]
			if len(self.template_list) > 1:
				cur_max_index, template_maxes = self._get_best_match(image)

			# Simply gets the max value and results of a single template
			else:
				results = self._match_template(image, self.template_list[1], "cv2.TM_CCOEFF")
				_, max_val, _, _ = cv2.minMaxLoc(results)
				template_maxes[0] = (results, max_val)

			self.cur_results = template_maxes[cur_max_index]
			self.cur_best_template = self.template_list[cur_max_index]

			if template_maxes[cur_max_index][1] < threshold: images_with_template.append(False)
			else: images_with_template.append(True)

		return images_with_template


class _VideoThreader(Thread, TemplateScanner):
	"""A private class to be used in conjunction with VideoScanner to scan a video across multiple threads
	"""
	def __init__(self, templates, video_path, frame_indexes, threshold, ouput_frames=False, file_naming_pattern="Level",
	             return_values=RETURN_TIMESTAMPS):
		Thread.__init__(self)
		TemplateScanner.__init__(self, templates=templates)
		self.video_path = video_path
		self.frame_indexes = frame_indexes
		self.threshold = threshold
		self.output_frames = ouput_frames
		self.output_generic = file_naming_pattern
		self.return_value = return_values
		self.output = []

	def _get_threshold(self):
		"""Sets output to a list of tuples (sum of all matches in frames, number of matches attempted)
		:return: None
		"""
		video = cv2.VideoCapture(self.video_path)
		video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_indexes[0])

		buffer_frames = 10
		frame_count = self.frame_indexes[1]

		assert frame_count > 0, "FRAME COUNT IS 0. PROBABLY A BROKEN FILE PATH."

		# Minus the frame count by 10 to give a little buffer room so that the video doesnt run out of frames)
		list_of_maxes = []
		frame_index = self.frame_indexes[0]
		number_scanned = 0
		while frame_index < (frame_count - buffer_frames):
			video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
			more_frames, frame = video.read()
			if not more_frames: break
			self.scan([frame])
			list_of_maxes.append(self.cur_results[1])
			number_scanned += 1
			frame_index += 10

		sum_and_length = (sum(list_of_maxes), number_scanned)
		self.output = sum_and_length
		del video

	def _get_timestamps(self):
		"""Sets output to a list of datetime.timedelta objects representing where a template was matched
		:return: None
		"""
		video = cv2.VideoCapture(self.video_path)

		threshold = self.threshold

		timestamps = []
		video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_indexes[0])

		# Slider as to not get all frames of a single jump, instead only getting as close to the first one as possible
		slider = [0, 0, 0, 0, 0, 0]

		# Slider to keep track of the image frames as corresponding to the original slider
		image_slider = [0, 0, 0, 0, 0, 0]

		# Defaults the skip index to -1 so as to not create an infinite loop
		skip_index = -1

		while True:

			# Read the current frame into greyscale
			more_frames, frame = video.read()

			if video.get(cv2.CAP_PROP_POS_FRAMES) < self.frame_indexes[1] and more_frames:

				# If the skip index is greater than 0, reset the sliders and increase the skip index
				if 0 <= skip_index <= len(slider):
					# slides the video forward
					_, _ = video.read()

					# increase the frame
					skip_index += 1
					frame += 1

					slider = [0, 0, 0, 0, 0, 0, 0]
					image_slider = [0, 0, 0, 0, 0, 0, 0]

					continue

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
					print(f"EXPORTING : {datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000)}")
					timestamps.append(datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000))

					# Get the frame of the first positive frame from the slider and export it
					index_of_positive = [index for index, value in enumerate(slider) if value == 1][0]
					self.scan([image_slider[index_of_positive]])

					if self.output_frames:
						frame_count = video.get(cv2.CAP_PROP_POS_FRAMES)
						self.plot_template_match(image_slider[index_of_positive], self.cur_results[0],
						                         output_title=f"{self.output_generic}{frame_count}")

					skip_index = 0
				frame += 1

			else:
				break

		self.output = timestamps

	def run(self):
		if self.return_value == RETURN_THRESHOLD:
			self._get_threshold()
		elif self.return_value == RETURN_TIMESTAMPS:
			self._get_timestamps()


class VideoScanner(TemplateScanner):
	def __init__(self, templates):
		"""defines a multi-threaded scanner
		:param templates: templates to scan videos with
		"""
		TemplateScanner.__init__(self, templates)  # While still a scanner, uses no methods in TemplateScanner
		self.output = []
		self.templates = templates  # Saves the file name for templates

	def _get_average_match(self, video, frame_indicies):
		"""Gets the average match on a video for a classes particular templates
		:param video: A cv2.VideoCapture object
		:return: A numerical value representing 5 steps above the average to be used as a threshold
		"""
		all_threads = []
		for frames in frame_indicies:
			current_threads = _VideoThreader(self.templates, video, frames, threshold=None,
			                     return_values=RETURN_THRESHOLD)
			all_threads.append(current_threads)
			current_threads.start()

		[i.join() for i in all_threads]  # joins all the threads returned by the VideoThreader
		all_sums = [j.output[0] for j in all_threads]
		all_lengths = [k.output[1] for k in all_threads]

		all_means = [s / l for s, l in zip(all_sums, all_lengths)]

		return sum(all_sums) / sum(all_lengths) + np.std(all_means) / 2

	def thread_scanners(self, video, divisor=400):
		"""Scans a passed video for the templates belonging to the instance
		:param video: A path to a video file (AVI, MP4, ETC)
		:param divisor: How many different threads to divide a video into (unit is frames)
		:return: a list of timestamps where a particular template was found
		"""
		loaded_video = cv2.VideoCapture(video)
		frame_count = loaded_video.get(cv2.CAP_PROP_FRAME_COUNT)
		frame_indices = []
		current_frame = 0
		while frame_count > divisor * len(frame_indices):
			frame_indices.append((current_frame, current_frame + divisor))
			current_frame += divisor

		thresh = self._get_average_match(video, frame_indices)

		for frames in frame_indices:
			print(f"SCANNING FRAMES: {frames}")
			threads = _VideoThreader(self.templates, video, frames, threshold=thresh)
			self.output.append(threads)
			threads.start()

		return self.output
