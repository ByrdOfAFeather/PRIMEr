let youtubeDL = require("youtube-dl");
let express = require('express');
let fs = require("fs");
let router = express.Router();
let sql = require("sqlite3");
let queue = require("../javascript/queuer.js");


router.put('/', function(req, res) {
    res.status(200).json(JSON.parse('{"status": "Successfully Received Data!"}'));

    let parsedData = JSON.parse(req.body["data"]);
    let videoID = parsedData["videoID"];
    let path = "VideoFiles/" + videoID + ".mp4";
    req.connection.setTimeout(120000*1000);

    let downloader = youtubeDL("https://www.youtube.com/watch?v=" + parsedData["videoID"], ['--format=18']);

    let size;
    downloader.on('info', function (info) {
        size = info.size;
        console.log('Download started');
    });

    downloader.pipe(fs.createWriteStream(path));

    // Source: https://stackoverflow.com/questions/49185538/how-to-add-progress-bar
    // let pos = 0;
    // let progress = 0;
    // downloader.on('data', (chunk) => {
    //     pos += chunk.length;
    //     if (size) {
    //         progress = (pos / size * 100).toFixed(2);
    //         console.log(progress);
    //     }
    // });

    downloader.on("end", function (info) {
        queue.addNew(parsedData);
    });
});

module.exports = router;
