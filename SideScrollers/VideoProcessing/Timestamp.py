class Timestamp:
	def __init__(self, marker, time):
		"""Class representing a time stamp
		:param marker: The char_descriptor for the time stamp
		:type marker: str
		:param time: The actual time stamp
		:type time: datetime.timedelta
		"""
		self.marker = marker
		self.time = time
