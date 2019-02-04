class Template:
	"""A class representing a template
	Attributes:
		id              integer value representing the actual id of the template in a database
		path            string representing the path to the template
		descriptor      string describing what the template is
	"""
	def __init__(self, template_id, path, descriptor):
		"""Initialization for Template
		:param template_id: The id for the template stored in the database
		:param path: The path to the image file
		:param descriptor: The text describing the template
		"""
		self.id = template_id
		self.path = path
		print(f"THIS IS THE PATHWAY {self.path}")
		self.descriptor = descriptor


