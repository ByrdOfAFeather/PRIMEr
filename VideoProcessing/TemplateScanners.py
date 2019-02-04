from VideoProcessing.Timestamp import Timestamp
from threading import Thread
import numpy as np
import datetime
import cv2

RETURN_TIMESTAMPS = 0
RETURN_THRESHOLD = 1


class TemplateScanner:
	"""A image scanner
	Attributes:
		template_list       A list of numpy matrices representing the templates
		cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		cur_results         The current result of the scan, used to find the threshold
	"""
	def __init__(self, templates, threshold=0):
		"""Initializer for TemplateScanner
		:param templates:  A dict in the style { descriptor: [ list of associated template paths ] }
		:type templates: dict
		"""
		self.templates = templates
		self.cur_best_template = None
		self.cur_results = None

		# Note that thresholds are built in the build_image_threshold_dict for efficiency reasons if set to None
		self.threshold = threshold if threshold else None
		self.templates = self._build_image_threshold_dict()

	def _build_image_threshold_dict(self):
		"""Builds dictionaries for Templates and optionally thresholds
		"""
		template_dict = {}
		thresholds = {}
		for name in self.templates.keys():
			template_dict[name] = []
			for templates in self.templates[name]:
				current_path = templates.path
				image_color = cv2.imread(f"{current_path}")
				assert image_color is not None, "IMAGE NOT FOUND IN PATH, ABORTING"

				image_color_flipped = cv2.flip(image_color, 1)
				template_dict[name].append(image_color)
				template_dict[name].append(image_color_flipped)
			if not self.threshold: thresholds[name] = 0

		if not self.threshold: self.threshold = thresholds
		return template_dict

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

	def _get_best_match(self, image):
		"""Gets the best match given a list of templates
		:param image: a numpy representation of an image that is to be scanned for templates
		:return: the index of best template and the results as well as maximum value of the template
		"""
		positive_matches = []
		all_template_maxes = {}
		for descriptor in self.templates.keys():
			all_template_maxes[descriptor] = None
			current_template_maxes = {}
			for template in self.templates[descriptor]:
				results = self._match_template(image, template, "cv2.TM_CCOEFF_NORMED")

				# Gets the highest template match value
				_, max_val, _, _ = cv2.minMaxLoc(results)
				current_template_maxes[max_val] = (results, max_val)

			best_match_for_current_descriptor = max(current_template_maxes.keys())
			self.cur_results = current_template_maxes[best_match_for_current_descriptor]

			if best_match_for_current_descriptor >= self.threshold:
				positive_matches.append((descriptor, best_match_for_current_descriptor))
				all_template_maxes[descriptor] = current_template_maxes[best_match_for_current_descriptor]

		if len(positive_matches) > 1:
			cur_max = 0
			cur_max_descriptor = ""
			for descriptor, match_value in positive_matches:
				if cur_max < match_value - self.threshold:
					cur_max = (match_value - self.threshold)
					cur_max_descriptor = descriptor

			self.cur_results = all_template_maxes[cur_max_descriptor]
			return cur_max_descriptor

		elif len(positive_matches) == 1:
			self.cur_results = all_template_maxes[positive_matches[0][0]]
			return positive_matches[0][0]

		else: return False

	def scan(self, image):
		"""Scans through the images passed to the original class and builds a list of T/F for if the template was found
		:param image:
		:type image:
		:return: List of the names of the descriptors found in the image
		"""
		cur_max_descriptor = self._get_best_match(image)
		return cur_max_descriptor


class VideoScanner(TemplateScanner):
	"""A Scanner Aimed at scanning a entire video
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		[Inherited] cur_results         The current result of the scan, used to find the threshold
	"""
	def __init__(self, templates):
		"""Initializer for VideoScanner
		:param templates:  A dict in the style { descriptor: [ list of associated template paths ] }
		:type templates: dict
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
			self.scan(frame)
			list_of_maxes.append(self.cur_results[1])

			i += 10

		# Reset the video
		video.set(1, 0)

		threshold = sum(list_of_maxes) / len(list_of_maxes)  # + (np.std(list_of_maxes))
		return threshold

	def scan_video(self, video):
		"""Scans a passed video for the templates belonging to the instance
		:param video: A path to a video file (AVI, MP4, ETC)
		:return: a list of timestamps where a particular template was found
		"""
		video = cv2.VideoCapture(video)
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
				export = self.scan(frame)

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
					self.scan(image_slider[index_of_positive])

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
		[Inherited] cur_results         The current result of the scan, used to find the threshold
		video_path                      A path to the video this scanner is responsible for scanning
		frame_indexes                   The part of the video this scanner is responsible for scanning
		file_naming_pattern             If outputting frame, the generic name for the outputted frames
		return_value                    The type of values to be returned (Threshold or Timestamps)
		output                          Due to the nature of threading, the return value for this thread, either a specific threashold or a list of timestamps
	"""
	def __init__(self, templates, video_path, frame_indexes,
	             threshold, return_values=RETURN_TIMESTAMPS
	             ):
		"""Initializer for _VideoThreader
		Parameters and their functions defined in class description
		:param templates:  A dict in the style { descriptor: [ list of associated template paths ] }
		:type templates: dict
		:type video_path: str
		:type frame_indexes: tuple
		:type return_values: int
		"""
		Thread.__init__(self)
		TemplateScanner.__init__(self, templates=templates)
		self.video_path = video_path
		self.frame_indexes = frame_indexes
		self.threshold = threshold
		self.return_value = return_values
		self.output = None

	def _get_timestamps(self):
		"""Sets output to a list of datetime.timedelta objects representing where a template was matched
		:return: None
		"""
		video = cv2.VideoCapture(self.video_path)

		timestamps = []
		video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_indexes[0])

		fps = video.get(cv2.CAP_PROP_FPS)

		# Slider as to not get all frames of a single template, instead only getting as close to the first one as possible
		sliders = {descriptor: [0, 0, 0, 0] for descriptor in self.templates.keys()}

		# Slider to keep track of the image frames as corresponding to the original slider
		image_slider = [0, 0, 0, 0]

		# Defaults the skip index to -1 so as to not create an infinite loop
		skip_index = -1

		while True:

			# Read the current frame into greyscale
			more_frames, frame = video.read()

			if video.get(cv2.CAP_PROP_POS_FRAMES) < self.frame_indexes[1] and more_frames:

				# If the skip index is greater than 0, reset the sliders and increase the skip index
				if 0 <= skip_index <= len(list(sliders.values())[0]):
					# slides the video forward
					_, _ = video.read()

					# increase the frame
					skip_index += 1
					np.add(frame, fps, casting="unsafe")

					sliders = {descriptor: [0, 0, 0, 0] for descriptor in self.templates.keys()}
					image_slider = [0, 0, 0, 0]

					continue

				# Add new items to the image slider
				image_slider.pop(0)
				image_slider.append(frame)

				# Get the export of the scanner
				export = self.scan(frame)

				# Slide the slider and get the average
				[sliders[descriptor].pop(0) for descriptor in self.templates.keys()]

				try:
					sliders[export].append(1)
					[sliders[descriptor].append(0) for descriptor in self.templates.keys()]

				except KeyError:
					[sliders[descriptor].append(0) for descriptor in self.templates.keys()]

				cur_average_max = 0
				cur_descriptor_max = ""
				for descriptor, slider in sliders.items():
					cur_average = sum(slider) / len(slider)
					if cur_average_max < cur_average:
						cur_average_max = cur_average
						cur_descriptor_max = descriptor

				# If the average value is greater than the threshold the template should be there
				if cur_average_max >= .5:
					print(f"EXPORTING : {datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000)}")
					print(f"EXPORTING : {cur_descriptor_max}")
					timestamps.append(Timestamp(cur_descriptor_max,
					                            datetime.timedelta(seconds=video.get(cv2.CAP_PROP_POS_MSEC) / 1000)))

					skip_index = 0
				np.add(frame, fps, casting="unsafe")

			else:
				break
		del video

		self.output = timestamps

	def run(self):
		if self.return_value == RETURN_TIMESTAMPS:
			self._get_timestamps()


class ThresholdFinder(TemplateScanner, Thread):
	"""A class that finds the threshold for individual templates
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific image [important when multiple templates represent the same thing]
		[Inherited] cur_results         The current result of the scan, used for plotting
		output                          The output of this class
		templates                       A container of the path values of the templates
	"""
	def __init__(self, templates, video, divisor=600):
		"""Initializer for VideoScannerThreaded
		Parameters and their functions defined in class description
		:type templates: dict
		"""
		TemplateScanner.__init__(self, templates)  # While still a scanner, uses no methods in TemplateScanner
		Thread.__init__(self)
		self.output = []
		self.video = video
		self.divisor = divisor
		self.templates = templates  # Saves the file name for templates

	def _get_average_match(self, video, frame_indicies):
		"""Gets the average match on a video for a classes particular templates
		:param video: A cv2.VideoCapture object
		:return: A numerical value representing 5 steps above the average to be used as a threshold
		"""
		all_threads = []
		assert frame_indicies, "NO FRAME INDICES WERE PASSED! BREAKING!"
		for frames in frame_indicies:
			current_threads = _VideoThreader(self.templates, video, frames, threshold=None,
			                                 return_values=RETURN_THRESHOLD, )
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

	def run(self):
		"""Scans a passed video for the templates belonging to the instance
		"""
		loaded_video = cv2.VideoCapture(self.video)

		frame_count = loaded_video.get(cv2.CAP_PROP_FRAME_COUNT)

		assert frame_count, "NO FRAMES WERE DETECTED! BREAKING!"

		frame_indices = []
		current_frame = 0

		while frame_count > self.divisor * len(frame_indices):
			frame_indices.append((current_frame, current_frame + self.divisor))
			current_frame += self.divisor

		self.output = self._get_average_match(self.video, frame_indices)


class VideoScannerThreaded(TemplateScanner):
	"""A class representing a threaded video scanner
	Attributes:
		[Inherited] template_list       A list of numpy matrices representing the templates
		[Inherited] cur_best_template   The numpy array of the best matched template given a specific ima
		[Inherited] cur_results         The current result of the scan, used for plotting
		output                          The output of this class
		templates                       A dict in the style { descriptor: [ list of templates associated ] }
		thresholds                      A dict in the style { descriptor: int value representing threshold }
	"""
	def __init__(self, templates, thresholds):
		"""Initializer for VideoScannerThreaded
		Parameters and their functions defined in class description
		:param templates:  A dict in the style { descriptor: [ list of associated template paths ] }
		:type templates: dict
		:param thresholds:  A dict in the style { descriptor: int value representing threshold }
		:type thresholds: dict
		"""
		TemplateScanner.__init__(self, templates)  # While still a scanner, uses no methods in TemplateSc
		self.output = []
		self.templates = templates  # Saves the file name for templates
		self.threshold = thresholds

	def thread_scanners(self, video, divisor=600):
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

		for frames in frame_indices:
			threads = _VideoThreader(self.templates, video, frames, self.threshold)
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
		:type templates: dict{str:Template}
		:type video: str
		"""
		assert len(templates) != 0, "Expected Template List Size Greater Than 0"
		Thread.__init__(self)
		self.templates = templates
		self.video_path = video
		self.output = []

	def run(self):
		threshold = .7
		scanner = VideoScannerThreaded(self.templates, threshold)
		scanner_threads = scanner.thread_scanners(self.video_path)
		[threads.join() for threads in scanner_threads]

		for times in scanner_threads:
			final_output = [time for time in times.output]
			self.output.extend(final_output)
