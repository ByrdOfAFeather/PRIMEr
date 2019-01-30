from VideoProcessing.Timestamp import Timestamp
from threading import Thread
import matplotlib.pyplot as plt
import numpy as np
import datetime
import cv2

RETURN_TIMESTAMPS = 0
RETURN_THRESHOLD = 1


class TemplateScanner:
	"""A image scanner that has the ability to plot its results
	Attributes:
		template_list       A list of numpy matrices representing the templates
		cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		cur_results         The current result of the scan, used for plotting
	"""
	def __init__(self, templates):
		"""Initializer for TemplateScanner
		:param templates: list of str values representing images that will be overridden with matrices
		:type templates: list[str]
		"""
		self.template_list = templates
		self.cur_best_template = None
		self.cur_results = None
		self.template_list = self._build_image_list(*self.template_list)

	def plot_template_match(self, image, template_results, title="Template Matching result", output_title="TEST"):
		"""Plots the image with the rectangle put on top of it. (Inspired from: https://docs.opencv.org/3.4.3/d4/dc6/tutorial_py_template_matching.html)
		:param image: A numpy representation of a image
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
		:param image: A numpy representation of a image
		:param template: Another numpy representation of a image that is scanned for in the other passed image
		:param filter_process: The type of cv2 equation to use (see: https://docs.opencv.org/3.4.3/df/dfb/group__imgproc__object.html#ga586ebfb0a7fb604b35a23d85391329be)
		:type filter_process: str
		:return: The results of a template match
		"""
		filter_process = eval(filter_process)
		return cv2.matchTemplate(image, template, filter_process)

	@staticmethod
	def _build_image_list(*image_names):
		"""Builds an array of templates based on the passed file names
		:param image_names: File names of templates
		:return: a template list of numpy arrays
		"""
		template_list = []
		for name in image_names:
			image_color = cv2.imread(f"{name}")
			image_color_flipped = cv2.flip(image_color, 1)
			template_list.append(image_color)
			template_list.append(image_color_flipped)
		return template_list

	def _get_best_match(self, image):
		"""Gets the best match given a list of templates
		:param image: a numpy representation of an image that is to be scanned for templates
		:return: the index of best template and the results as well as maximum value of the template
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
		:type image_list: list
		:param threshold: The numeric value at which a template match is to be considered a negative
		:type threshold: int
		:return: boolean list of true or false describing when an image was found
		"""
		# Loops through all the images
		images_with_template = []
		for image in image_list:
			template_maxes = {}
			cur_max_index = 0

			# Loops through all the filter images and finds the most similar one to the current photo [Multi template]
			if len(self.template_list) > 1: cur_max_index, template_maxes = self._get_best_match(image)

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


class VideoScanner(TemplateScanner):
	"""A Scanner Aimed at scanning a entire video
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		[Inherited] cur_results         The current result of the scan, used for plotting
	"""
	def __init__(self, templates):
		"""Initializer for VideoScanner
		:param templates: list of str values representing images that will be overridden with matrices
		:type templates: list[str]
		"""
		TemplateScanner.__init__(self, templates)

	def _get_average_match(self, video):
		"""Gets the average match on a video for a classes particular templates
		:param video: A cv2.VideoCapture object
		:return: A numerical value representing 2 standard deviations above the average to be used as a threshold
		"""
		buffer_frames = 10
		frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

		assert frame_count > 0, "FRAME COUNT IS 0. PROBABLY A BROKEN FILE PATH."

		# Minus the frame count by 10 to give a little buffer room so that the video doesnt run out of frames)
		list_of_maxes = []
		i = 0
		while i < (frame_count - buffer_frames):
			video.set(1, i)
			_, frame = video.read()
			self.scan([frame])
			list_of_maxes.append(self.cur_results[1])

			i += 10

		# Reset the video
		video.set(1, 0)

		threshold = sum(list_of_maxes) / len(list_of_maxes) + (np.std(list_of_maxes))
		return threshold

	def scan_video(self, video, output_generic="", save_frames=False):
		"""Scans a passed video for the templates belonging to the instance
		:param video: A path to a video file (AVI, MP4, ETC)
		:param output_generic: The generic output file name for each frame where a template is found
		:param save_frames: If set to true each positive frame will be exported as an image
		:return: a list of timestamps where a particular template was found
		"""
		video = cv2.VideoCapture(video)
		threshold = self._get_average_match(video)
		timestamps = []

		frame_counter = 0

		# Slider as to not get all frames of a single jump, instead only getting as close to the first one as possible
		slider = [0, 0, 0, 0, 0, 0, 0]

		# Slider to keep track of the image frames as corresponding to the original slider
		image_slider = [0, 0, 0, 0, 0, 0, 0]

		# Defaults the skip index to -1 as to not create an infinite loop
		skip_index = -1

		while True:

			# If the skip index is greater than 0, reset the sliders and increase the skip index
			if 0 <= skip_index <= len(slider):

				# slides the video forward
				_, _ = video.read()

				# increase the frame
				skip_index += 1
				frame += 1

				slider = [0, 0, 0, 0, 0, 0, 0, 0]
				image_slider = [0, 0, 0, 0, 0, 0, 0, 0]

				continue

			# Read the current frame into greyscale
			more_frames, frame = video.read()

			if more_frames:
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
					timestamps.append(datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000))

					print(f"This is the time in the video at which this frame is exported "
					      f"{datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000)} ")

					# Get the frame of the first positive frame from the slider and export it
					index_of_positive = [index for index, value in enumerate(slider) if value == 1][0]
					self.scan([image_slider[index_of_positive]])

					if save_frames:
						self.plot_template_match(image_slider[index_of_positive], self.cur_results[0],
						                         output_title=f"{output_generic}{frame_counter}")

					skip_index = 0
				frame_counter += 1

			else:
				break

		return timestamps


class _VideoThreader(Thread, TemplateScanner):
	"""A private class to be used in conjunction with VideoScanner to scan a video across multiple threads
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		[Inherited] cur_results         The current result of the scan, used for plotting
		video_path                      A path to the video this scanner is responsible for scanning
		frame_indexes                   The part of the video this scanner is responsible for scanning
		output_frames                   If it should output frames [DEPRECIATED]
		file_naming_pattern             If outputting frame, the generic name for the outputted frames
		return_value                    The type of values to be returned (Threshold or Timestamps)
		output                          Due to the nature of threading, the return value for this thread, either a specific threashold or a list of timestamps
	"""
	def __init__(self, templates, video_path, frame_indexes,
	             threshold, output_frames=False, file_naming_pattern="Level",
	             return_values=RETURN_TIMESTAMPS
	             ):
		"""Initializer for _VideoThreader
		Parameters and their functions defined in class description
		:type templates: list[str]
		:type video_path: str
		:type frame_indexes: tuple
		:type output_frames: bool
		:type file_naming_pattern: str
		:type return_values: int
		"""
		Thread.__init__(self)
		TemplateScanner.__init__(self, templates=templates)
		self.video_path = video_path
		self.frame_indexes = frame_indexes
		self.threshold = threshold
		self.output_frames = output_frames
		self.output_generic = file_naming_pattern
		self.return_value = return_values
		self.output = None

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
		slider = [0, 0, 0, 0, 0, 0, 0, 0]

		# Slider to keep track of the image frames as corresponding to the original slider
		image_slider = [0, 0, 0, 0, 0, 0, 0, 0]

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

					slider = [0, 0, 0, 0, 0, 0, 0, 0, 0]
					image_slider = [0, 0, 0, 0, 0, 0, 0, 0, 0]

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

				# If the average value is greater than the threshold the template should be there
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
		del video

		self.output = timestamps

	def run(self):
		if self.return_value == RETURN_THRESHOLD:
			self._get_threshold()
		elif self.return_value == RETURN_TIMESTAMPS:
			self._get_timestamps()


class VideoScannerThreaded(TemplateScanner):
	"""A class representing a threaded video scanner
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		[Inherited] cur_results         The current result of the scan, used for plotting
		output                          The output of this class
		templates                       A container of the path values of the templates
		output_frames                   If it should output frames [DEPRECIATED]
	"""
	def __init__(self, templates, output_frames=False):
		"""Initializer for VideoScannerThreaded
		Parameters and their functions defined in class description
		:type templates: list[str]
		:type output_frames: bool
		"""
		TemplateScanner.__init__(self, templates)  # While still a scanner, uses no methods in TemplateScanner
		self.output = []
		self.templates = templates  # Saves the file name for templates
		self.output_frames = output_frames

	def _get_average_match(self, video, frame_indicies):
		"""Gets the average match on a video for a classes particular templates
		:param video: A cv2.VideoCapture object
		:return: A numerical value representing 5 steps above the average to be used as a threshold
		"""
		all_threads = []
		assert frame_indicies, "NO FRAME INDICES WERE PASSED! BREAKING!"
		for frames in frame_indicies:
			current_threads = _VideoThreader(self.templates, video, frames, threshold=None,
			                                 return_values=RETURN_THRESHOLD, output_frames=self.output_frames)
			all_threads.append(current_threads)
			current_threads.start()
		print(f"=== STARTING {len(all_threads)} THREADS ===")
		[i.join() for i in all_threads]  # joins all the threads returned by the VideoThreader
		all_sums = [j.output[0] for j in all_threads]
		all_lengths = [k.output[1] for k in all_threads]

		all_means = [s / l for s, l in zip(all_sums, all_lengths)]

		print(f" === THIS IS THREASH: "
		      f"{sum(all_sums) / sum(all_lengths) + np.std(all_means)} ===")
		return sum(all_sums) / sum(all_lengths) + np.std(all_means)

	def thread_scanners(self, video, divisor=400):
		"""Scans a passed video for the templates belonging to the instance
		:param video: A path to a video file (AVI, MP4, ETC)
		:param divisor: How many different threads to divide a video into (unit is frames)
		:return: a list of timestamps where a particular template was found
		"""
		loaded_video = cv2.VideoCapture(video)

		frame_count = loaded_video.get(cv2.CAP_PROP_FRAME_COUNT)

		assert frame_count, "NO FRAMES WERE DETECTED! BREAKING!"

		frame_indices = []
		current_frame = 0
		while frame_count > divisor * len(frame_indices):
			frame_indices.append((current_frame, current_frame + divisor))
			current_frame += divisor

		thresh = self._get_average_match(video, frame_indices)

		for frames in frame_indices:
			threads = _VideoThreader(self.templates, video, frames, threshold=thresh)
			self.output.append(threads)
			threads.start()

		return self.output


class ThreadedVideoScan(Thread):
	"""Allows for multiple templates representing different things to scan the video at the same time
	Attributes:
		templates   A list of template objects
		video_path  A path to the video that this thread is responsible for
		output      Due to the nature of threads, the output of the run function
	"""
	def __init__(self, templates, video):
		"""Initialization for ThreadedVideoScanner
		Parameters and their functions defined in class description
		:type templates: list[Template]
		:type video: str
		"""
		assert len(templates) != 0, "Expected Template List Size Greater Than 0"
		Thread.__init__(self)
		self.templates = templates
		self.video_path = video
		self.output = []

	def run(self):
		path_list = []
		template_marker = self.templates[0].char_descriptor
		for templates in self.templates: path_list.append(templates.path)
		finder = VideoScannerThreaded(templates=path_list)

		finder = finder.thread_scanners(f"{self.video_path}")
		for threads in finder:
			threads.join()

		for times in finder:
			final_output = [Timestamp(template_marker, times) for times in times.output]
			self.output.extend(final_output)

