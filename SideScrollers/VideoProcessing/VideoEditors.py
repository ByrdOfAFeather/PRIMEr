from .TemplateScannersThreaded import VideoScannerThreaded


class VideoEditor:
	def __init__(self, video, templates):
		"""Initialization of the class
		:param video: Path to a video
		:type video: str
		:param templates: Path to templates
		:type templates: list
		"""
		self.video = video
		self.templates = templates

	def edit(self, templates):
		for template in templates:
			current_scanner = VideoScannerThreaded(template)
			scanner_results = current_scanner.thread_scanners(self.video)

			for threads in scanner_results:
				threads.join()
