// Credit
// @Speencer Lockhart
// https://stackoverflow.com/questions/17408010/drawing-a-rectangle-using-click-mouse-move-and-click

initDraw(document.getElementById("video-container"));

let previous_rectangle = null;

function initDraw(canvas) {

    var mouse = {
        x: 0,
        y: 0,
        startX: 0,
        startY: 0
    };

    function setMousePosition(e) {
        var ev = e || window.event;
        if (ev.pageX) {
            mouse.x = ev.pageX + window.pageXOffset;
            mouse.y = ev.pageY + window.pageYOffset;
        } else if (ev.clientX) {
            mouse.x = ev.clientX + document.body.scrollLeft;
            mouse.y = ev.clientY + document.body.scrollTop;
        }
    }

    var element = null;

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
        if (element !== null) {
            previous_rectangle = element;
            element = null;
            canvas.style.cursor = "default";
        } else {
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