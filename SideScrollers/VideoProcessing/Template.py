
import sqlite3


class Template:
	def __init__(self, template_id,  database_path):
		self.id = template_id
		self.database_path = database_path
		self.char_descriptor = self._get_char_descriptor()

	def _get_char_descriptor(self):
		db = sqlite3.connect(self.database_path)
		cursor = db.cursor()
		cursor.execute(f"""SELECT DESCRIPTOR FROM TEMPLATEPATHS WHERE TEMPLATEID = {self.id}""")
		results = cursor.fetchall()
		results = results[0][0]  # The sql returns in a tuple in a list
		return results


test = Template(1, "/home/byrdofafeather/OneDrive/ByrdOfAFeather/Python/PRIMEr/WebServer/pathDB.db")

