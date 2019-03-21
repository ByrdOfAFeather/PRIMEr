// Credit
// @Speencer Lockhart
// https://stackoverflow.com/questions/17408010/drawing-a-rectangle-using-click-mouse-move-and-click

// initDraw(document.getElementById("video-container"));

let previous_rectangle = null;
let canDraw = false;

function initDraw(canvas) {
    var mouse = {
        x: 0,
        y: 0,
        startX: 0,
        startY: 0
    };

    function setMousePosition(e) {
        var ev = e;
        mouse.x = ev.pageX;
        mouse.y = ev.pageY;
    }

    var element = null;

    canvas.onmousemove = function (e) {
        setMousePosition(e);

        if (element !== null) {
            element.style.width = Math.abs(mouse.x - mouse.startX) + 'px';
            element.style.height = Math.abs(mouse.y - mouse.startY) + 'px';
            element.style.left = (mouse.x - mouse.startX < 0) ? mouse.x + 'px' : mouse.startX + 'px';
            element.style.top = (mouse.y - mouse.startY < 0) ? mouse.y + 'px' : mouse.startY + 'px';
            // element.style.left = document.getElementById("current-video").left + element.style.left;
            // element.style.top = document.getElementById("current-video").top + element.style.top;
        }
    };


    canvas.onclick = function (_) {
        let current_video = document.getElementById("output-screengrab");
        if (_.target !== current_video && element === null) {}
        else if (element !== null) {
            if (parseInt(element.style.height, 10) <= parseInt(current_video.height, 10) &&
            parseInt(element.style.width, 10) <= parseInt(current_video.width, 10)) {
                previous_rectangle = element;
                element = null;
                canvas.style.cursor = "default";
            }
            else {}
        }

        else {
            if (previous_rectangle !== null) { previous_rectangle.remove(); }

            mouse.startX = mouse.x;
            mouse.startY = mouse.y;

            element = document.createElement('div');
            element.className = 'rectangle';
            element.style.left = mouse.x + 'px';
            element.style.top = mouse.y + 'px';

            canvas.appendChild(element);
            canvas.style.cursor = "crosshair";
        }
    };
}

function getPreviousRectangle() { return previous_rectangle.parentNode; }