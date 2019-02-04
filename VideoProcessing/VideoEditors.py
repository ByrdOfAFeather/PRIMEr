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
		self.timepoints = []

	def get_nearest_descriptors(self, start_index, max_time_from_current):
		"""IMPLEMENTATION LEFT TO SUBCLASSES
		:type start_index: int
		:type max_time_from_current: datetime.timedelta
		:return: list containing timestamps of nearest actions
		"""
		pass

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):
		"""IMPLEMENTATION LEFT TO
		:type current_class: str
		:type index_of_timestamps: int
		:type nearest_times: list
		:return: dictionary containing choices based on the current class and it's nearest actions
		"""

	def edit(self):
		"""Builds a JSON list of edits that can be interpreted by https://tarheelgameplay.org
		:return: JSON formatted dictionary representing edits
		"""
		all_markers = []
		for timestamp in self.timestamps:
			if timestamp.marker not in all_markers:
				all_markers.append(timestamp.marker)

		# Context information (top of the JSON)
		game_information = {
			"videoId": f"{self.video_id}",
			"start": 0,
			"vocabulary": f"{all_markers}".replace("[", "").replace("]", "").replace(",", "").replace("'", ""),
			"tags": ["advanced"],
			"kind": "advanced",
			# "duration": int(self.timestamps[-1].time.total_seconds()),
			"dof": len(all_markers),
		}

		print("=== STARTING EDITING INFORMATION ===")
		print(f"NUMBER OF UNIQUE TEMPLATE DESCRIPTORS: {len(all_markers)}")
		print(f"TEMPLATE DESCRIPTORS: {all_markers}")
		print(f"NUMBER OF TEMPLATE POSITIVES RETURNED: {len(self.timestamps)}")
		print(f"THIS IS THE LIST OF TIMESTAMPS: {[i.time.total_seconds() for i in self.timestamps]}")
		print("=== END EDITING INFORMATION ===")

		self.index = 0
		while self.index < len(self.timestamps) - 1:
			current_class = self.timestamps[self.index].marker

			nearest_times = self.get_nearest_descriptors(self.index, datetime.timedelta(seconds=4))
			if nearest_times == self.FINAL_ITEM_IN_LIST: break
			if nearest_times == self.NO_APPLICABLE_CHOICES:
				self.index += 1
				continue

			[self.timepoints.append(i) for i in self.build_choices_json(current_class, self.index, nearest_times)]
			self.index += len(nearest_times) + 1

		game_information["timePoints"] = self.timepoints
		game_information["hits"] = len(self.timepoints)
		return game_information


class VanillaEditor(_VideoEditor):
	def __init__(self, timestamps, video_id):
		_VideoEditor.__init__(self, timestamps, video_id)

	def get_nearest_descriptors(self, start_index, max_time_from_current):

		# If the index is right at the end of the list, there aren't anymore actions after it
		if start_index + 1 >= len(self.timestamps) - 1:
			return self.FINAL_ITEM_IN_LIST

		# If the next action is the current action, move to the next action
		if self.timestamps[start_index].marker == self.timestamps[start_index + 1].marker:
			self.index += 1
			return self.get_nearest_descriptors(start_index + 1, max_time_from_current)

		sub_timestamps = self.timestamps[start_index:]
		delete_list = []
		end_index = 0
		for index, timestamps in enumerate(sub_timestamps):
			# Remove any items that are the same action as the starting action, as long as they have a different time
			if timestamps.marker == self.timestamps[start_index].marker \
					and timestamps is not self.timestamps[start_index]:
				delete_list.append(timestamps)

			# Sets the end index after the time is reached
			if timestamps.time - self.timestamps[start_index].time >= max_time_from_current:
				end_index = index + start_index
				break

		return_list = self.timestamps[start_index:end_index]
		return_list = [item for item in return_list if item not in delete_list]
		if not return_list: return self.NO_APPLICABLE_CHOICES
		return return_list

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):
		# Set basic choice to keep doing what is already being done
		choices = [
			{
				# TODO: Investigate the possibility of using NLP to add "keep" to special cases, ex: "Keep Running"
				"prompt": current_class,
				"next": round(self.timestamps[index_of_timestamps].time.total_seconds(), 1)
			}
		]

		# Builds a choice for every unique action in the nearest times
		descriptor_tracker = []
		for nearby_time in nearest_times[1:]:
			if nearby_time.marker not in descriptor_tracker:
				choices.append(
					{
						"prompt": nearby_time.marker,
						"next": round(nearby_time.time.total_seconds(), 1)
					}
				)
			descriptor_tracker.append(nearby_time.marker)

		return [
			{
				"time": round(self.timestamps[index_of_timestamps].time.total_seconds(), 1),
				"choices": choices
			}
		]


class ConditionalEditor(_VideoEditor):
	"""An editor based on the idea of conditional choices
	Attributes:
		FINAL_ITEM_IN_LIST      A constant representing one of two cases in which editing needs to be broken [out of items]
		NO_APPLICABLE_CHOICES   A constant representing the case in which there are no nearby templates found
		video_id                The youtube ID of the video currently being edited
		timestamps              A list of timestamps with their markers, which is what the edit is based on
		specials                A dictionary describing special types of timestamps
	"""
	def __init__(self, timestamps, video_id, specials):
		_VideoEditor.__init__(self, timestamps, video_id,)
		specials["Punishment"] = datetime.timedelta(seconds=specials["Punishment"][0]).total_seconds()
		self.specials = specials
		self.punishment_offset = 0
		self.punishment_length = 1

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

			# If the time stamps are nearing the specials, return what is already provided
			specials_at_index = abs(timestamps.time.total_seconds() - self.specials["Punishment"]) <= 4
			if specials_at_index:
				end_index = index + start_index
				break

		return_list = self.timestamps[start_index:end_index]
		return_list = [item for item in return_list if item not in delete_list]
		if not return_list: return self.NO_APPLICABLE_CHOICES
		print(f"this is return list {[i.marker for i in return_list]}")
		return return_list

	def build_choices_json(self, current_class, index_of_timestamps, nearest_times):

		# this is used to make multiple "Continue" choices near the punishment timestamp so that they can point to
		# different points in the video. (This is needed so the video can go right back to where a mistake was made)
		self.punishment_offset += .2
		incorrect_time = round((self.specials["Punishment"] - self.punishment_offset + self.punishment_length) - .1, 1)

		if len(nearest_times) == 1:
			choices = [
				{
					# TODO: Investigate the possibility of using NLP to add "keep" to special cases, ex: "Keep Running"
					"prompt": nearest_times[0].marker,
					"next": nearest_times[0].time.total_seconds() + .1
				}
			]

		else:
			choices = [
				{
					# TODO: Investigate the possibility of using NLP to add "keep" to special cases, ex: "Keep Running"
					"prompt": nearest_times[0].marker,
					"next": incorrect_time
				}
			]

			descriptor_tracker = []
			for index, nearby_time in enumerate(nearest_times[1:]):
				if nearby_time.marker not in descriptor_tracker:
					if index == 0:
						choices.append(
							{
								"prompt": nearby_time.marker,
								"next": round(nearest_times[0].time.total_seconds() + .1, 2)
							}
						)

					else:
						choices.append(
							{
								"prompt": nearby_time.marker,
								"next": incorrect_time
							}
						)

				descriptor_tracker.append(nearby_time.marker)

		return [
			{
				"time": round(self.timestamps[index_of_timestamps].time.total_seconds(), 2),
				"choices": choices
			},
			{
				"time": round((self.specials["Punishment"] - self.punishment_offset + self.punishment_length), 2),
				"choices": [
					{
						"prompt": "Continue",
						"next": round(self.timestamps[index_of_timestamps].time.total_seconds() - .1, 2)
					}
				]
			}
		]

	def edit(self):
		edits = super(ConditionalEditor, self).edit()

		# This time point is so that the player can skip over the punishment "Continues" while playing through the video
		edits["timePoints"].append({
				"time": round(self.specials["Punishment"] - self.punishment_offset + self.punishment_length - .2, 1),
				"choices": [
					{
						"prompt": "Continue",
						"next": round(
							self.specials["Punishment"] + 2,
							1
						)
					}
				]
			}
		)
		return edits






