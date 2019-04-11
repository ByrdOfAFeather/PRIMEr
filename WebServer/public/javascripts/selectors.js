// Credit
// @Speencer Lockhart
// https://stackoverflow.com/questions/17408010/drawing-a-rectangle-using-click-mouse-move-and-click

let previous_rectangle = null;

function initDraw(canvas) {
    let mouse = {
        x: 0,
        y: 0,
        startX: 0,
        startY: 0
    };

    function setMousePosition(e) {
        let ev = e;
        mouse.x = ev.pageX;
        mouse.y = ev.pageY;
    }

    let element = null;

    canvas.onmousemove = function (e) {
        setMousePosition(e);

        if (element !== null) {
            element.style.width = Math.abs(mouse.x - mouse.startX) + 'px';
            element.style.height = Math.abs(mouse.y - mouse.startY) + 'px';
            element.style.left = (mouse.x - mouse.startX < 0) ? mouse.x + 'px' : mouse.startX + 'px';
            element.style.top = (mouse.y - mouse.startY < 0) ? mouse.y + 'px' : mouse.startY + 'px';
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

function getPreviousRectangle() {
    if (previous_rectangle == null) {
        return null;
    }
    else {
        return previous_rectangle.parentNode;
    }
}