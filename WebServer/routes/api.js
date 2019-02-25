let PythonShell = require('python-shell');
let express = require('express');
let router = express.Router();


/* GET home page. */
router.put('/', function(req, res) {
    console.log(req);
    console.log(req.body["data"]);
    options = {
        mode: 'text',
        pythonPath: '/home/byrdofafeather/VirtualEnviroments/PRIMEr/bin/python3.7',
        pythonOptions: ['-u'], // get print results in real-time
        args: [req.body["data"]]
    };
    PythonShell.PythonShell.run("api_nodejs_test.py", options, function(err) {
        if (err) { throw err; }
        console.log("FINISHED");


    });
    console.log(JSON.parse(req.body["data"]));

    // res.render('index', { title: 'Express' });
});

module.exports = router;
