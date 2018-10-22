import sqlite3 as sql
from flask import Flask, request
from flask_restful import Resource, Api


primer_server = Flask(__name__)
primer_api = Api(primer_server)
template_dictionary = {}


def add_items(data_to_add):
	db = sql.connect("pathDB.db")
	cursor = db.cursor()
	params = ("VIDEOPATH", "TEMPLATESPATH")
	values = (data_to_add["video"], data_to_add["templates"])
	cursor.execute(f"""INSERT INTO EDITDATA {params} VALUES {values}""")
	db.commit()
	db.close()


class EditEndPoint(Resource):
	def __int__(self):
		Resource.__init__(self)

	@staticmethod
	def get():
		pass

	@staticmethod
	def put():
		parsed_data = {}
		raw_data = request.form["data"]
		parsed_data["video"] = raw_data.split(":")[1].split(",")[0]
		parsed_data["templates"] = raw_data.split(":")[2].replace('}', '')
		add_items(parsed_data)
		return {"added_data": parsed_data}


primer_api.add_resource(EditEndPoint, "/add")


def run():
	primer_server.run(port="5002")


if __name__ == "__main__": run()