let PythonShell = require('python-shell');
let youtubeDL = require("youtube-dl");
let express = require('express');
let fs = require("fs");
let router = express.Router();


router.put('/', function(req, res) {
    req.connection.setTimeout(120000*1000);
    let options = {
        mode: 'text',
        pythonPath: '/home/byrdofafeather/VirtualEnviroments/PRIMEr/bin/python3.7',
        pythonOptions: ['-u'],
        args: [req.body["data"]]
    };

    let jsonData = JSON.parse(req.body["data"]);
    let videoID = jsonData["videoID"];
    let path = "VideoFiles/" + videoID + ".mp4";
    if (fs.existsSync(path)) {
        console.log("VIDEO ALREADY DOWNLOADED!");
        PythonShell.PythonShell.run("api_nodejs_test.py", options, function (err, results) {
            if (err) {
                throw err;
            }
            let splicedValues = results.splice(results.length - 10, results.length);
            console.log(splicedValues);
            console.log("FINISHED");
            json = JSON.parse('{"video":true, "link":' + '"' +splicedValues[splicedValues.length - 2] + '"' + '}');
            res.status(200).json(json);
        });
    }

    else {
        let downloader = youtubeDL("https://www.youtube.com/watch?v=" + videoID, ['--format=18']);

        let size;
        downloader.on('info', function (info) {
            size = info.size;
            console.log('Download started');
        });

        downloader.pipe(fs.createWriteStream(path));

        let pos = 0;
        let progress = 0;
        // Source: https://stackoverflow.com/questions/49185538/how-to-add-progress-bar
        downloader.on('data', (chunk) => {
            pos += chunk.length;
            if (size) {
                progress = (pos / size * 100).toFixed(2);
                console.log(progress);
            }
        });

        downloader.on("end", function (info) {
            PythonShell.PythonShell.run("api_nodejs_test.py", options, function (err, results) {
                if (err) {
                    throw err;
                }
                let splicedValues = results.splice(results.length - 10, results.length);
                console.log(splicedValues);
                console.log("FINISHED");
                json = JSON.parse('{"video":true, "link":' + '"' + splicedValues[splicedValues.length - 2] + '"' + '}');
                res.status(200).json(json);
            });
        });
    }
});

module.exports = router;
