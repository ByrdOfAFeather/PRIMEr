let sql = require("sqlite3");
let PythonShell = require('python-shell');
let fs = require("fs");

let currentlyRemoving = false;
let currentlyInserting = false;
let currentDelete = 0;
let removed = 0;


class Queue {
	constructor() {
		this.queue = [];
	}

	enqueue(item) {
		this.queue.push(item);
	}

	dequeue() {
		return this.queue.pop();
	}

	size() {
		return this.queue.length;
	}
}


class Database {

	constructor(databasePath) {
		this.dbPath = databasePath;
		let database = new sql.Database(this.dbPath);
		database.run('PRAGMA journal_mode = WAL;');
		database.close();
	}


	writeResult(json) {
		console.log("THIS A JSON")
		console.log(json);
		let link = json["link"]
		let connection = new sql.Database(this.dbPath);
		connection.run("INSERT INTO RESULTS(LINK) VALUES(?)", {1: link}, function (err) {
			if (err) {
				console.log(err);
			}
			else {
				console.log("SUCCESSFULLY INSERTED RESULTS");
			}
		});
		connection.close();
	}


	insertNewVideoData(json) {
		let path = "VideoFiles/" + json["videoID"] + ".mp4";
		let dbPath = this.dbPath;
		let insertTemplateFunction = this.insertNewTemplateData;
		let queueFunction = this.insertNewQueueData;
		let connection = new sql.Database(dbPath);
		console.log("INSERTING INTO VIDEOPATHS");
		connection.run('INSERT INTO VIDEOPATHS(VIDEOPATH) VALUES(?)', {1: path}, function (err) {
			if (err) {
				console.log("Error in inserting into video paths");
				console.log(err);
			}
			else {
				if (this.lastID) {
					let newID = this.lastID;
					console.log("FINISHED INSERTING INTO VIDEOPATHS");
					insertTemplateFunction(newID, json, dbPath, queueFunction);
				}
			}
		});
		connection.close();
	}


	static cleanString(stringData) {
		return stringData.replace(" ", "").replace("<", "")
		.replace(">", "")
		.replace("\"", "")
		.replace("/", "")
		.replace("\\", "")
		.replace("|", "")
		.replace("?", "")
		.replace("*", "");
	}


	insertNewTemplateData(newID, json, dbPath, queueFunction) {
		let templates = json["templates"];
		let keys = Object.keys(templates);
		let connection = new sql.Database(dbPath);
		console.log("INSERTING INTO TEMPLATE DATA");

		connection.serialize(function () {
			let insertedIntoQueue = false;
			for (let i = 0; i < keys.length; i++) {
				let currentTemplate = keys[i];
				let safeName = Database.cleanString(currentTemplate);

				let templateStoragePath = "TemplateFiles/" + json["videoID"] + "/" + safeName;
				if (!fs.existsSync("TemplateFiles")) {
					fs.mkdirSync("TemplateFiles");
				}
				if (!fs.existsSync("TemplateFiles/" + json["videoID"])) {
					fs.mkdirSync("TemplateFiles/" + json["videoID"]);
				}
				if (!fs.existsSync(templateStoragePath)) {
					fs.mkdirSync(templateStoragePath);
				}

				let insert = connection.prepare("INSERT INTO TEMPLATEPATHS (TEMPLATEPATH, VIDEOID, DESCRIPTOR, DATA) VALUES (?, ?, ?, ?)");
				for (let j = 0; j < json["templates"][currentTemplate].length; j++) {
					let path = templateStoragePath + "/" + j + ".png";
					console.log("RUNNING SERIALIZED FUNCTION " + j);
					insert.run(path, newID, safeName, JSON.stringify(json["templates"][currentTemplate][j]), function (err) {
						if (err) {
							console.log("Error at inserting SERIALIZED data");
						}
					});
					console.log("FINISHED SERIALIZED FUNCTION " + j);
				}

				insert.finalize(function () {
					if (!insertedIntoQueue) {
						queueFunction(newID, dbPath);
						insertedIntoQueue = true;
					}
				});
				console.log("FINISHED INSERTING TEMPLATE DATA");
			}
		});
		connection.close();
	}


	insertNewQueueData(newID, dbPath) {
		let connection = new sql.Database(dbPath);
		console.log("INSERTING INTO QUEUE");
		connection.run("INSERT INTO QUEUE(VIDEOID) VALUES(?)", {
			1: newID
		}, function (err) {
			if (err) {
				console.log("Error at inserting into queue");
				console.log(err);
			}
			else {
				console.log("FINISHED INSERTING!");
				currentlyInserting = false;
				callInterval.dbInsertHandler = setInterval(insertQueue, 100);
			}
		});
		connection.close();
	}


	getNextQueue() {
		console.log("GETTING MAX ID");
		this.getNextQueueID();
	}


	getNextQueueID() {
		let connection = new sql.Database(this.dbPath);
		let nextVideoID = this.getNextVideoID;
		let startScanFunction = this.startScan;
		connection.each("SELECT MAX(QUEUEID) FROM QUEUE", function (err, id) {
			if (!err) {
				console.log(id);
				console.log("GETTING VIDEOID FROM MAXID");
				nextVideoID(id["MAX(QUEUEID)"], connection, startScanFunction);
			}
			else {
				console.log("ERROR READING MAX ID");
				console.log(err);
			}
		});
	}


	getNextVideoID(queueID, connection, startScanFunction) {
		let startScan = startScanFunction;
		connection.all("SELECT VIDEOID from QUEUE where QUEUEID = ?", {1: queueID}, function (err, videoID) {
			if (!err) {
				if (!videoID.length) {
					console.log("There appear to be no more videos!");
					callInterval.dbRemoveHandler = setInterval(queueHandler, 15000);
					currentlyRemoving = false;
					connection.close();
				}
				else {
					console.log("FINISHED GETTING VIDEOID DATA");
					currentDelete = queueID;
					let passVideoID = videoID[0]["VIDEOID"];
					startScan(passVideoID);
					connection.close();
				}
			}
			else {
				console.log("Error reading video from queue");
				console.log(err);
				connection.close();
				return false;
			}
		});
	}


	deleteQueue(id) {
		let connection = new sql.Database(this.dbPath);
		console.log("DELETING FROM QUEUE");
		connection.run("DELETE FROM QUEUE WHERE QUEUEID = ?", {1: id}, function (err) {
			if (err) {
				console.log(err);
			}
			console.log("FINISHED DELETING FROM QUEUE");
			currentlyRemoving = false;
		});
		connection.close();
	}


	startScan(videoID) {
		let options = {
			mode: 'text',
			pythonPath: '/home/byrdofafeather/VirtualEnviroments/PRIMEr/bin/python3.7',
			pythonOptions: ['-u'],
			args: [videoID]
		};

		PythonShell.PythonShell.run("editor.py", options, Database.afterPython).on('message', function (message) {
			console.log(message);
		});
	}


	static afterPython(err, results) {
		if (err) {
			throw err;
		}
		queue.deleteQueue(currentDelete);
		let splicedValues = results.splice(results.length - 10, results.length);
		console.log(splicedValues);
		console.log("FINISHED");
		let json = JSON.parse('{"video":true, "link":' + '"' + splicedValues[splicedValues.length - 2] + '"' + '}');
		queue.writeResult(json);
		// fs.unlink(path, function (err) {
		//     if (err) {
		//         console.log(err);
		//     } else {
		//         console.log("VIDEO " + videoID + " Deleted!");
		//     }
		// });

		// queue.deleteLastQueue();
		// // queue.writeResult(json);
		callInterval.dbRemoveHandler = setInterval(queueHandler, 15000);
	}
}


let queue = new Database("./pathDB.db");
let callInterval = {};
callInterval.dbRemoveHandler = setInterval(queueHandler, 15000);
callInterval.dbInsertHandler = setInterval(insertQueue, 10000);
let dbQueue = new Queue();


function insertQueue() {
	clearInterval(callInterval.dbInsertHandler);
	if (!currentlyRemoving && !currentlyInserting) {
		if (dbQueue.size() !== 0) {
			console.log("STARTING INSERT PROCESS");
			removed += 1;
			currentlyInserting = true;
			queue.insertNewVideoData(dbQueue.dequeue());
		}
		else {
			callInterval.dbInsertHandler = setInterval(insertQueue, 10000);

		}
	}
	else {
		callInterval.dbInsertHandler = setInterval(insertQueue, 10000);

	}
}

function queueHandler() {
	clearInterval(callInterval.dbRemoveHandler);

	if (currentlyInserting || currentlyRemoving) {
		callInterval.dbRemoveHandler = setInterval(queueHandler, 15000);
	}

	else {
		currentlyRemoving = true;
		console.log("STARTING REMOVE QUEUE HANDLER");
		queue.getNextQueue();
	}
}

function addNew(requestData) {
	dbQueue.enqueue(requestData);
}


module.exports = {addNew};