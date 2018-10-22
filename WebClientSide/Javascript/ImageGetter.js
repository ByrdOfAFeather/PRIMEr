// CREDIT (Inspired from)
// Kaiido
// https://stackoverflow.com/a/41195171/8448827
function screenshot(element, options = {}) {
    let cropper = document.createElement('canvas').getContext('2d');

    let finalWidth = options.width;
    let finalHeight = options.height;

    return html2canvas(element, options).then(c => {
        cropper.canvas.width = finalWidth;
        cropper.canvas.height = finalHeight;
        cropper.drawImage(c, 0, 0);
        console.log("THIS IS RECTANGLE X " + (+options.x));
        console.log("THIS IS RECTANGLE Y " + (+options.y));

        console.log(cropper.canvas);
        return cropper.canvas;
    });
}

function test() {
    let container = getPreviousRectangle();

    let rectangle = container.getElementsByClassName('rectangle')[0];
    let rectangleX = parseInt(rectangle.style.left, 10);
    let rectangleY = parseInt(rectangle.style.top, 10);
    let rectangleHeight = parseInt(rectangle.style.height, 10);
    let rectangleWidth = parseInt(rectangle.style.width, 10);

    let canvas = document.getElementById("test-canvas");
    let ctx = canvas.getContext("2d");
    let v = document.getElementById("current-video");

    console.log(v);

    // CREDIT
    // Brain Mayo
    // https://dev.to/protium/javascript-rendering-videos-with-html2canvas-3bk
    let w = v.videoWidth;
    let h = v.videoHeight;
    canvas.width = w;
    canvas.height = h;
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(v, 0, 0, w, h);
    v.style.backgroundImage = `url(${canvas.toDataURL()})`;
    v.style.backgroundSize = 'cover';
    ctx.clearRect(0, 0, w, h);
    // END CREDIT

    screenshot(document.body, {
        x: rectangleX,
        y: rectangleY,
        width: rectangleWidth,
        height: rectangleHeight,
        useCORS: true,
        allowTaint: true
    }).then(
        function (canvas) {
            var a = document.createElement('a');
            a.href = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");;
            document.body.appendChild(canvas);
            a.download = 'somefilename.png';
            a.click();
        }
    )
}

// END CREDIT