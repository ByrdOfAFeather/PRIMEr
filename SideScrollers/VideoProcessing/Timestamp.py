class Timestamp:
	"""Represents a single time stamp for easy access between the type of timestamp and the actual time of it
	Attributes:
		marker  The type of the timestamp, specified by the template that was found at the timestamp
		time    The time at which the template was found
	"""
	def __init__(self, marker, time):
		"""Class representing a time stamp
		:param marker: The char_descriptor for the time stamp
		:type marker: str
		:param time: The actual time stamp
		:type time: datetime.timedelta
		"""
		self.marker = marker
		self.time = time

