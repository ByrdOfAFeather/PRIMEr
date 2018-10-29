import sqlite3


class Template:
	def __init__(self, template_id,  database_path):
		self.id = template_id
		self.database_path = database_path
		self.path = self._general_get("TEMPLATEPATH")
		self.char_descriptor = self._general_get("DESCRIPTOR", strip=False)

	def _general_get(self, selection, strip=True):
		db = sqlite3.connect(self.database_path)
		cursor = db.cursor()
		cursor.execute(f"""SELECT {selection} FROM TEMPLATEPATHS WHERE TEMPLATEID = (?)""", (self.id,))
		results = cursor.fetchall()
		results = results[0][0]  # The sql returns in a tuple in a list
		if strip: results = results.lstrip()
		return results