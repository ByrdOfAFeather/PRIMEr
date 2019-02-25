let currentTemplateType = null;
let currentVideo = null;
let actionTemplateDict = {};
let conditionals = {};
let currentTime = null;
let templatesShowing = false;
let templateTable = document.getElementById("template-table");

// CREDIT (Inspired from)
// Kaiido
// https://stackoverflow.com/a/41195171/8448827
function screenshot(element, options = {}, set_id=false) {
    let cropper = document.createElement('canvas').getContext('2d');
    if (set_id) {
        cropper.canvas.id = "output-screengrab";
    }

    let finalWidth = options.width;
    let finalHeight = options.height;

    return html2canvas(element, options).then(c => {
        cropper.canvas.width = finalWidth;
        cropper.canvas.height = finalHeight;
        cropper.drawImage(c, 0, 0);
        return cropper.canvas;
    });
}

function exportTemplate() {
    let container = getPreviousRectangle();

    let rectangle = container.getElementsByClassName('rectangle')[0];
    let rectangleX = parseInt(rectangle.style.left, 10);
    let rectangleY = parseInt(rectangle.style.top, 10);
    let rectangleHeight = parseInt(rectangle.style.height, 10);
    let rectangleWidth = parseInt(rectangle.style.width, 10);
    rectangle.style.border = "none";

    let canvas = document.getElementById("output-screengrab");
    let ctx = canvas.getContext("2d");
    let v = document.getElementById("output-screengrab");


    // CREDIT
    // Brain Mayo
    // https://dev.to/protium/javascript-rendering-videos-with-html2canvas-3bk
    let w = v.width;
    let h = v.height;
    canvas.width = w;
    canvas.height = h;
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(v, 0, 0, w, h);
    v.style.backgroundImage = `url(${canvas.toDataURL()})`;
    canvas.height = 0;
    canvas.width = 0;
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
            if (!currentTemplateType) { alert("Please selection an action type before saving an action!"); }

            if (document.getElementById(currentTemplateType.toLowerCase()).classList[0] === "conditional-action-type") {
                conditionals[currentTemplateType] = [];
                conditionals[currentTemplateType].push(currentTime);
            }

            else {
                let image = canvas.toDataURL();
                let modImage = image.slice(22);
                try {
                    actionTemplateDict[currentTemplateType].push(modImage);
                }
                catch (TypeError) {
                    actionTemplateDict[currentTemplateType] = [];
                    actionTemplateDict[currentTemplateType].push(modImage);
                }
                finally {
                    let templateTableRow = document.getElementById(currentTemplateType + "-table");
                    let templatesAlreadyAdded = document.getElementsByClassName(currentTemplateType + "-data").length;
                    let newTemplate = document.createElement("td");
                    newTemplate.id = currentTemplateType + "-" + templatesAlreadyAdded;
                    newTemplate.className = currentTemplateType + "-data";
                    newTemplate.appendChild(canvas);
                    templateTableRow.appendChild(newTemplate);
                }
            }
        }
    )
}

function grabScreen() {
    let video = document.getElementById('current-video');

    let videoX = video.offsetLeft;
    let videoY = video.offsetTop;
    let videoHeight = video.videoHeight
    let videoWidth = video.videoWidth;

    let canvas = document.getElementById("output-screengrab");
    let ctx = canvas.getContext("2d");

    // CREDIT
    // Brain Mayo
    // https://dev.to/protium/javascript-rendering-videos-with-html2canvas-3bk
    canvas.width = videoWidth;
    canvas.height = videoHeight;
    ctx.fillRect(0, 0, videoWidth, videoHeight);
    ctx.drawImage(video, 0, 0, videoWidth, videoHeight);
    video.style.backgroundImage = `url(${canvas.toDataURL()})`;
    canvas.height = 0;
    canvas.width = 0;
    video.style.backgroundSize = 'cover';
    ctx.clearRect(0, 0, videoWidth, videoHeight);
    // END CREDIT

    console.log(document.readyState === "complete");
    screenshot(document.body, {
        x: videoX,
        y: videoY,
        width: videoWidth,
        height: videoHeight,
        useCORS: true
    }, true).then(
        function (canvas) {
            currentTime = document.getElementById("current-video").currentTime;
            let currentScreenCap = document.getElementById("output-screengrab");
            if (currentScreenCap) {
                currentScreenCap.parentNode.removeChild(currentScreenCap);
            }
            let screengrabContainer = document.getElementById("screengrab-container");
            screengrabContainer.appendChild(canvas);
            initDraw(screengrabContainer);
        }
    )
}

function setCurrentTemplateType(clickEvent) {
    let selector = document.getElementById("template-drop-down-button");
    if (typeof clickEvent === typeof "") {
        currentTemplateType = clickEvent;
        selector.innerText = clickEvent;
    }

    else if (clickEvent.target.tagName === "IMG") {
        currentTemplateType = "";
        selector.innerText = "Select Action Type";
        return;
    }

    else {
        currentTemplateType = clickEvent.target.text;
        selector.innerText = currentTemplateType;
    }
}

function deleteTemplate(event) {
    let currentActionTypeToDeleteNode = event.target.parentNode;
    if (currentActionTypeToDeleteNode.classList[0] === "conditional-action-type") {
        delete actionTemplateDict[currentActionTypeToDeleteNode.innerText];
        actionTemplateDict[currentActionTypeToDeleteNode] = [];
    }
    else {
        document.getElementById("template-drop-down-contents").removeChild(currentActionTypeToDeleteNode);
        delete actionTemplateDict[currentActionTypeToDeleteNode.innerText];
    }
}

function addNewTemplate() {
    let templateNameInput = document.getElementById("new-template-type");
    let newTemplateType = templateNameInput.value;

    if (document.getElementById(newTemplateType.toLowerCase())) {
        alert("You can't add a template with the same name twice!");
    }

    else {
        templateNameInput.value = "";
        let addedTemplateType = document.createElement("a");
        addedTemplateType.href = "#";
        addedTemplateType.onclick = function (event) {
            setCurrentTemplateType(event);
        };
        addedTemplateType.id = newTemplateType.toLowerCase();
        addedTemplateType.textContent = newTemplateType;
        setCurrentTemplateType(newTemplateType);

        let templateImage = document.createElement("img");
        templateImage.className = "delete-button";
        templateImage.src = "../static/Resources/deletebutton.png";
        templateImage.alt = "delete";
        templateImage.onclick = function (event) {
            event.preventDefault();
            deleteTemplate(event);
        };
        addedTemplateType.appendChild(templateImage);
        document.getElementById("template-drop-down-contents").prepend(addedTemplateType);

        // Add to the table data
        let newRow = document.createElement("tr");
        let baseData = document.createElement("td");
        let baseDataText = document.createTextNode(newTemplateType);
        baseData.appendChild(baseDataText);
        newRow.appendChild(baseData);
        newRow.id = newTemplateType + "-table";
        templateTable.appendChild(newRow);
    }
}

function showTemplates() {
    let templateDiv = document.getElementById("added-templates");
    templateDiv.style.display = templatesShowing ? "none" : "block";
    templatesShowing = !templatesShowing;
}

function showDropDown(passedButton) {
    console.log(passedButton.value);
    if (passedButton === document.getElementById("template-drop-down-button")) {
        document.getElementById("template-drop-down-contents").classList.toggle("show");
    }

    else if (passedButton === document.getElementById("show-templates")) {
        document.getElementById("templates-drop-down-contents").classList.toggle("show");
    }
}

function loadVideo() {
    let input = document.getElementById("input-video");
    let link = input.value;
    if (link.slice(0, 32) !== "https://www.youtube.com/watch?v=") {
        alert("Please input a valid Youtube URL!")
    }
    else {
        let linkID = link.slice(32);
        currentVideo = linkID;
    }
}

window.onclick = function(event) {
    if (!event.target.matches('.drop-down')) {
        let dropdowns = document.getElementsByClassName("drop-down-contents");
        let i;
        for (i = 0; i < dropdowns.length; i++) {
            let openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
};

window.onkeypress = function(event) {
    if (event.key === "Enter" && event.target === document.getElementById("new-template-type")) {
        addNewTemplate();
    }
};

function finish() {
    let data = {};
    data["templates"] = actionTemplateDict;
    data["conditionals"] = conditionals;
    console.log(data);
    data["videoID"] = currentVideo;
    let json = JSON.stringify(data);
    console.log(json);
    $.ajax({
        url: 'http://127.0.0.1:5001/api/startedit/',
        method: 'PUT',
        dataType: 'json',
        data: {
            data: json
        },
        success : function (results) {
            alert("Your video is now being processed! This could take a while.");
        },
        error : function(results) {
            if (results.status === 0) {
                alert("The API isn't currently running!");
            }
            else {
                alert("Something went wrong! Make sure you have added action templates!");
                console.log(results);
            }
        }
    });
}