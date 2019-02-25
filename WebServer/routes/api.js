let PythonShell = require('python-shell');
let youtubeDL = require("youtube-dl");
let express = require('express');
let fs = require("fs");
let router = express.Router();


/* GET home page. */
router.put('/', function(req, res) {
    let options = {
        mode: 'text',
        pythonPath: '/home/byrdofafeather/VirtualEnviroments/PRIMEr/bin/python3.7',
        pythonOptions: ['-u'], // get print results in real-time
        args: [req.body["data"]]
    };
    let json = JSON.parse(req.body["data"]);

    let videoID = json["videoID"];
    let downloader = youtubeDL("https://www.youtube.com/watch?v=" + videoID, ['--format=134']);

    downloader.on('info', function (info) {
        console.log('Download started');
        console.log('filename: ' + info._filename);
    });

    downloader.pipe(fs.createWriteStream("VideoFiles/" + videoID + '.mp4'));

    downloader.on("end", function (info) {
        PythonShell.PythonShell.run("api_nodejs_test.py", options, function (err, results) {
            if (err) {
                throw err;
            }
            console.log(results.splice(results.length - 10, results.length));
            console.log("FINISHED");
        });
        console.log(req.body["data"]);
        console.log(JSON.parse(req.body["data"]));
    });
});

module.exports = router;
