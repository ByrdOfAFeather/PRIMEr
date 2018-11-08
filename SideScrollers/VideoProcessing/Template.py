import sqlite3
import codecs


class Template:
	"""A class representing a template
	Attributes:
		id              integer value representing the actual id of the template in a database
		database_path   string representing the path to the database which contains the template
		path            string representing the local path to the template image
	"""
	def __init__(self, template_id,  database_path):
		"""Initialization for Template
		:param template_id: the id for the template stored in the database
		:param database_path: the path to the database containing the template
		"""
		self.id = template_id
		self.database_path = database_path
		self.path = self._general_get("TEMPLATEPATH")
		print(f"THIS IS THE PATHWAY {self.path}")
		self.char_descriptor = self._general_get("DESCRIPTOR", strip=False)

	def _general_get(self, selection, strip=True):
		"""gets information from the database
		:param selection: what should be got from the database
		:param strip: if spaces should be stripped from the begging and end
		:return: results based on selection of type str
		"""
		db = sqlite3.connect(self.database_path)
		cursor = db.cursor()
		cursor.execute(f"""SELECT {selection} FROM TEMPLATEPATHS WHERE TEMPLATEID = (?)""", (self.id,))
		results = cursor.fetchall()
		results = results[0][0]  # The sql returns in a tuple in a list
		if strip: results = results.lstrip()
		return results
