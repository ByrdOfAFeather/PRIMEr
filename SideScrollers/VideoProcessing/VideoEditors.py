import datetime


class VideoEditor:
	def __init__(self, video, templates, timestamps):
		"""Initialization of the class
		:param video: Path to a video
		:type video: str
		:param templates: Path to templates
		:type templates: list
		"""
		self.video = video
		self.templates = templates
		self.timestamps = timestamps
		self.possible_descriptors = self._get_possible_descriptors()

	def _get_possible_descriptors(self):
		possible_descriptors = [i.char_descriptor for i in self.templates]
		return possible_descriptors

	def get_nearest_descriptors(self, start_index, max_time_from_current):

		if self.timestamps[start_index].char_descriptor == self.timestamps[start_index + 1].char_descriptor:
			self.get_nearest_descriptors(start_index + 1, max_time_from_current)

		sub_timestamps = self.timestamps[start_index:]
		delete_indexes = []
		end_index = 0

		for index, timestamps in enumerate(sub_timestamps):
			if timestamps.char_descriptor == self.timestamps[start_index].char_descriptor:
				delete_indexes.append(index)

			if timestamps.time - self.timestamps[start_index].time >= max_time_from_current:
				end_index = index

		return_list = self.timestamps[start_index:end_index]
		for delete_items in delete_indexes:
			del return_list[delete_items]

		return return_list

	def edit(self):
		print("=== STARTING EDITING INFORMATION ===")
		print(f"NUMBER OF UNIQUE TEMPLATE DESCRIPTORS: {len(self.possible_descriptors)}")
		print(f"TEMPLATE DESCRIPTORS: {self.possible_descriptors}")
		print(f"NUMBER OF TEMPLATE POSITIVES RETURNED: {len(self.timestamps)}")
		print("=== END EDITING INFORMATION ===")

		timepoints = []
		index_of_timestamps = 0
		while index_of_timestamps < len(self.timestamps):
			current_class = self.timestamps[index_of_timestamps].marker

			nearest_descriptors = self.get_nearest_descriptors(index_of_timestamps, datetime.timedelta(seconds=1))
			choices = []
			for descriptor in nearest_descriptors:
				choices.append(
					{
						"prompt": descriptor.char_descriptor,
						"next": descriptor.time
					}
				)
			choices.append(
				{
					"prompt": current_class,
					"next": self.timestamps[index_of_timestamps].time
				}
			)

			timepoints.append(
				{
						"time": self.timestamps[index_of_timestamps].time,
						"choices": choices
				}
			)
			index_of_timestamps += len(nearest_descriptors)

