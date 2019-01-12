import datetime


class VideoEditor:
	"""A class representing a video editor
	Attributes:
		FINAL_ITEM_IN_LIST      A constant representing one of two cases in which editing needs to be broken [out of items]
		NO_APPLICABLE_CHOICES   A constant representing the case in which there are no nearby templates found
		video                   The path to the video for which this is responsible for editing
		timestamps              A list of timestamps with their markers, which is what the edit is based on
	"""
	def __init__(self, video, timestamps, video_id):
		"""Initialization of the class
		:type video: int
		:type timestamps: list[Timestamp]
		:type video_id: str
		"""
		self.FINAL_ITEM_IN_LIST = -1
		self.NO_APPLICABLE_CHOICES = -2
		self.video = video
		self.timestamps = timestamps
		self.video_id = video_id

	def get_nearest_descriptors(self, start_index, max_time_from_current):
		if start_index + 1 >= len(self.timestamps) - 1:
			return self.FINAL_ITEM_IN_LIST

		if self.timestamps[start_index].marker == self.timestamps[start_index + 1].marker:
			self.get_nearest_descriptors(start_index + 1, max_time_from_current)

		sub_timestamps = self.timestamps[start_index:]
		delete_list = []
		end_index = 0

		multi_commands = []
		for index, timestamps in enumerate(sub_timestamps):
			if timestamps.marker == self.timestamps[start_index].marker:
				delete_list.append(timestamps)

			if timestamps.time - self.timestamps[start_index].time >= max_time_from_current:
				end_index = index + start_index
				break

		if multi_commands: pass

		return_list = self.timestamps[start_index:end_index]
		return_list = [item for item in return_list if item not in delete_list]
		if not return_list: return self.NO_APPLICABLE_CHOICES
		print("this is start index", start_index)
		print("this is end index", end_index)
		print(f"this is return list {return_list}")
		return return_list

	def edit(self):
		all_markers = []
		for timestamp in self.timestamps:
			if timestamp.marker not in all_markers:
				all_markers.append(timestamp.marker)

		print(self.timestamps[-1].time)

		game_information = {
			"videoId": f"{self.video_id}",
			"start": 0,
			"vocabulary": f"{all_markers}".replace("[", "").replace("]", "").replace(",", "").replace("'", ""),
			"tags": ["advanced"],
			"kind": "advanced",
			"duration": int(self.timestamps[-1].time.total_seconds()),
			"dof": 2,
		}

		print("=== STARTING EDITING INFORMATION ===")
		print(f"NUMBER OF UNIQUE TEMPLATE DESCRIPTORS: {len(all_markers)}")
		print(f"TEMPLATE DESCRIPTORS: {all_markers}")
		print(f"NUMBER OF TEMPLATE POSITIVES RETURNED: {len(self.timestamps)}")
		print("=== END EDITING INFORMATION ===")

		timepoints = []
		index_of_timestamps = 0
		while index_of_timestamps < len(self.timestamps) - 1:
			current_class = self.timestamps[index_of_timestamps].marker

			nearest_times = self.get_nearest_descriptors(index_of_timestamps, datetime.timedelta(seconds=4))
			print(nearest_times)
			if nearest_times == self.FINAL_ITEM_IN_LIST: break
			if nearest_times == self.NO_APPLICABLE_CHOICES:
				index_of_timestamps += 1
				continue

			choices = [
				{
					"prompt": current_class,
					"next": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2)
				}
			]

			descriptor_tracker = []
			for nearby_time in nearest_times:
				if nearby_time.marker not in descriptor_tracker:
					choices.append(
						{
							"prompt": nearby_time.marker,
							"next": round(nearby_time.time.total_seconds(), 2)
						}
					)
				descriptor_tracker.append(nearby_time.marker)

			timepoints.append(
				{
					"time": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2),
					"choices": choices
				}
			)

			index_of_timestamps += len(nearest_times) + 1

		game_information["timePoints"] = timepoints
		game_information["hits"] = len(timepoints)
		return game_information

