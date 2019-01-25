import datetime


class _VideoEditor:
	"""A class representing a video editor
	Attributes:
		FINAL_ITEM_IN_LIST      A constant representing one of two cases in which editing needs to be broken [out of items]
		NO_APPLICABLE_CHOICES   A constant representing the case in which there are no nearby templates found
		video_id                The youtube ID of the video currently being edited
		timestamps              A list of timestamps with their markers, which is what the edit is based on
	"""
	def __init__(self, timestamps, video_id):
		"""Initialization of the class
		:type timestamps: list[Timestamp]
		:type video_id: str
		"""
		self.FINAL_ITEM_IN_LIST = -1
		self.NO_APPLICABLE_CHOICES = -2
		self.timestamps = timestamps
		self.video_id = video_id
		self.index = 0

	def get_nearest_descriptors(self, start_index, max_time_from_current):
		"""IMPLEMENTATION LEFT TO SUBCLASSES"""
		pass

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):
		"""IMPLEMENTATION LEFT TO SUBCLASSES"""

	def edit(self):
		all_markers = []
		for timestamp in self.timestamps:
			if timestamp.marker not in all_markers:
				all_markers.append(timestamp.marker)

		game_information = {
			"videoId": f"{self.video_id}",
			"start": 0,
			"vocabulary": f"{all_markers}".replace("[", "").replace("]", "").replace(",", "").replace("'", ""),
			"tags": ["advanced"],
			"kind": "advanced",
			"duration": int(self.timestamps[-1].time.total_seconds()),
			"dof": len(all_markers),
		}

		print("=== STARTING EDITING INFORMATION ===")
		print(f"NUMBER OF UNIQUE TEMPLATE DESCRIPTORS: {len(all_markers)}")
		print(f"TEMPLATE DESCRIPTORS: {all_markers}")
		print(f"NUMBER OF TEMPLATE POSITIVES RETURNED: {len(self.timestamps)}")
		print("=== END EDITING INFORMATION ===")

		timepoints = []
		self.index = 0
		while self.index < len(self.timestamps) - 1:
			current_class = self.timestamps[self.index].marker

			nearest_times = self.get_nearest_descriptors(self.index, datetime.timedelta(seconds=4))
			if nearest_times == self.FINAL_ITEM_IN_LIST: break
			if nearest_times == self.NO_APPLICABLE_CHOICES:
				self.index += 1
				continue

			[timepoints.append(i) for i in self.build_choices_json(current_class, self.index, nearest_times)]
			self.index += len(nearest_times) + 1

		game_information["timePoints"] = timepoints
		game_information["hits"] = len(timepoints)
		return game_information


class VanillaEditor(_VideoEditor):
	"""A class representing a video editor
	Attributes:
		FINAL_ITEM_IN_LIST      A constant representing one of two cases in which editing needs to be broken [out of items]
		NO_APPLICABLE_CHOICES   A constant representing the case in which there are no nearby templates found
		video                   The path to the video for which this is responsible for editing
		timestamps              A list of timestamps with their markers, which is what the edit is based on
	"""
	def __init__(self, timestamps, video_id):
		_VideoEditor.__init__(self, timestamps, video_id)

	def get_nearest_descriptors(self, start_index, max_time_from_current):
		if start_index + 1 >= len(self.timestamps) - 1:
			return self.FINAL_ITEM_IN_LIST

		if self.timestamps[start_index].marker == self.timestamps[start_index + 1].marker:
			self.index += 1
			return self.get_nearest_descriptors(start_index + 1, max_time_from_current)

		sub_timestamps = self.timestamps[start_index:]
		delete_list = []
		end_index = 0

		for index, timestamps in enumerate(sub_timestamps):
			if timestamps.marker == self.timestamps[start_index].marker \
					and timestamps is not self.timestamps[start_index]:
				delete_list.append(timestamps)

			if timestamps.time - self.timestamps[start_index].time >= max_time_from_current:
				end_index = index + start_index
				break

		return_list = self.timestamps[start_index:end_index]
		return_list = [item for item in return_list if item not in delete_list]
		if not return_list: return self.NO_APPLICABLE_CHOICES
		print("this is start index", start_index)
		print("this is end index", end_index)
		print(f"this is return list {[i.marker for i in return_list]}")
		return return_list

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):
		choices = [
			{
				# TODO: Investigate the possibility of using NLP to add "keep" to special cases, ex: "Keep Running"
				"prompt": current_class,
				"next": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2)
			}
		]

		descriptor_tracker = []
		for nearby_time in nearest_times[1:]:
			print(f"THIS IS THE CURRENT DESCRIPTOR TRACKER {descriptor_tracker}")
			if nearby_time.marker not in descriptor_tracker:
				print(f"THIS IS THE CURRENT MARKER {nearby_time.marker}")
				choices.append(
					{
						"prompt": nearby_time.marker,
						"next": round(nearby_time.time.total_seconds(), 2)
					}
				)
			descriptor_tracker.append(nearby_time.marker)

		print(f"THIS IS CHOICES {choices}")
		return [
			{
				"time": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2),
				"choices": choices
			}
		]


class ConditionalEditor(VanillaEditor):
	"""BASE COMPARISION: https://tarheelgameplay.org/play/?key=table-aroma-nikita
	"""
	def __init__(self, timestamps, video_id, specials):
		_VideoEditor.__init__(self, timestamps, video_id,)
		specials["Punishment"] = datetime.timedelta(seconds=specials["Punishment"][0])
		specials["Victory"] = datetime.timedelta(seconds=specials["Victory"][0])
		specials["Failure"] = datetime.timedelta(seconds=specials["Failure"][0])
		self.specials = specials
		self.punishment_offset = datetime.timedelta(microseconds=0)
		self.punishment_length = datetime.timedelta(seconds=1)

	def get_nearest_descriptors(self, start_index, max_time_from_current):
		if start_index + 1 >= len(self.timestamps) - 1:
			return self.FINAL_ITEM_IN_LIST

		if self.timestamps[start_index].marker == self.timestamps[start_index + 1].marker:
			self.index += 1
			return self.get_nearest_descriptors(start_index + 1, max_time_from_current)

		sub_timestamps = self.timestamps[start_index:]
		delete_list = []
		end_index = 0

		for index, timestamps in enumerate(sub_timestamps):
			if timestamps.marker == self.timestamps[start_index].marker \
					and timestamps is not self.timestamps[start_index]: delete_list.append(timestamps)

			if timestamps.time - self.timestamps[start_index].time >= max_time_from_current:
				end_index = index + start_index
				break

			specials_at_index = (timestamps.time - self.specials["Punishment"] >= datetime.timedelta(seconds=4) or
				timestamps.time - self.specials["Victory"] >= datetime.timedelta(seconds=4) or
				timestamps.time - self.specials["Failure"] >= datetime.timedelta(seconds=4))

			if specials_at_index:
				end_index = index + start_index
				break

		print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
		print(f"THIS IS DELETE LIST: {delete_list}")
		return_list = self.timestamps[start_index:end_index]
		print(f"THIS IS RETURN LIST {return_list}")
		return_list = [item for item in return_list if item not in delete_list]
		if not return_list: return self.NO_APPLICABLE_CHOICES
		print("this is start index", start_index)
		print("this is end index", end_index)
		print(f"this is return list {[i.marker for i in return_list]}")
		return return_list

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):
		choices = [
			{
				# TODO: Investigate the possibility of using NLP to add "keep" to special cases, ex: "Keep Running"
				"prompt": nearest_times[0].marker,
				"next": round(nearest_times[0].time.total_seconds(), 2)
			}
		]

		descriptor_tracker = []
		for nearby_time in nearest_times[1:]:
			if nearby_time.marker not in descriptor_tracker:
				choices.append(
					{
						"prompt": nearby_time.marker,
						"next": round(self.specials["Punishment"].total_seconds(), 2)
					}
				)

			descriptor_tracker.append(nearby_time.marker)
			self.punishment_offset += datetime.timedelta(milliseconds=100)

		return [
			{
				"time": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2),
				"choices": choices
			},
			{
				"time": round((self.specials["Punishment"] - self.punishment_offset +
				              self.punishment_length).total_seconds(), 2),
				"choices": [
					{
						"prompt": "Continue",
						"next": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2)
					}
				]
			}
		]




