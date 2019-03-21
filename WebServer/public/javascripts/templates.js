let currentTemplateType = null;
let currentVideo = null;
let actionTemplateDict = {};
let conditionals = {};
let currentTime = null;
let templatesShowing = false;
let templateTable = document.getElementById("template-table");
let videoID = "";
let orgVideoWidth;
let orgVideoHeight;

let video = document.getElementById("current-video");
video.onpause = function() {
    grabScreen();
};

function exportTemplate() {
    let container = getPreviousRectangle();

    let rectangle = container.getElementsByClassName('rectangle')[0];
    let rectangleX = parseInt(rectangle.style.left, 10);
    let rectangleY = parseInt(rectangle.style.top, 10);
    let rectangleHeight = parseInt(rectangle.style.height, 10);
    let rectangleWidth = parseInt(rectangle.style.width, 10);
    rectangle.style.border = "none";

    let canvas = document.createElement("canvas");
    let ctx = canvas.getContext("2d");
    let v = document.getElementById("output-screengrab");

    canvas.width = rectangleWidth;
    canvas.height = rectangleHeight;
    canvas.style.height = rectangleHeight + "px";
    canvas.style.width = rectangleWidth + "px";

    let position = $("#output-screengrab").offset();

    ctx.fillRect(0, 0, rectangleWidth, rectangleHeight);
    ctx.drawImage(v, rectangleX - position["left"], rectangleY - position["top"], rectangleWidth , rectangleHeight, 0, 0, rectangleWidth, rectangleHeight);

    if (!currentTemplateType) { alert("Please selection an action type before saving an action!"); }

    if (document.getElementById(currentTemplateType.toLowerCase()).classList[0] === "conditional-action-type") {
        conditionals[currentTemplateType] = [];
        conditionals[currentTemplateType].push(currentTime);
    }

    else {
        realRectX = rectangleX - position["left"];
        realRectY = rectangleY - position["top"];
        let currentFrame = currentTime;
        try {
            actionTemplateDict[currentTemplateType].push({realRectX,
                realRectY,
                rectangleHeight,
                rectangleWidth,
                currentFrame});
        }
        catch (TypeError) {
            actionTemplateDict[currentTemplateType] = [];
            actionTemplateDict[currentTemplateType].push({realRectX,
                realRectY,
                rectangleHeight,
                rectangleWidth,
                currentFrame});
        }
        finally {
            let templateTableRow = document.getElementById(currentTemplateType + "-table");
            let templatesAlreadyAdded = document.getElementsByClassName(currentTemplateType + "-data").length;
            let newTemplate = document.createElement("td");
            newTemplate.id = currentTemplateType + "-" + templatesAlreadyAdded;
            newTemplate.className = currentTemplateType + "-data";
            newTemplate.appendChild(canvas);
            let templateImage = document.createElement("img");
            templateImage.className = "delete-button";
            templateImage.src = "http://i.imgur.com/TWLiACv.png";
            templateImage.alt = "delete";
            templateImage.onclick = function (event) {
                event.preventDefault();
                deleteTemplate(event, true);
            };
            newTemplate.appendChild(templateImage);
            templateTableRow.appendChild(newTemplate);
        }
    }
}

function grabScreen() {
    let videoWidth;
    let videoHeight;
    let video = document.getElementById('current-video');

    if (video.videoWidth / video.videoHeight !== 16/9) {
        videoHeight = video.videoHeight;
        videoWidth = video.videoWidth;
    }
    else {
        videoHeight = video.offsetHeight;
        videoWidth = video.offsetWidth;
    }

    let canvas = document.getElementById("output-screengrab");
    let ctx = canvas.getContext("2d");

    canvas.width = videoWidth;
    canvas.height = videoHeight;
    canvas.style.width = videoWidth + "px";
    canvas.style.height = videoHeight + "px";

    ctx.fillRect(0, 0, videoWidth, videoHeight);
    ctx.drawImage(video, 0, 0, videoWidth, videoHeight);

    currentTime = document.getElementById("current-video").currentTime;
    let currentScreenCap = document.getElementById("output-screengrab");
    if (currentScreenCap) {
        currentScreenCap.parentNode.removeChild(currentScreenCap);
    }
    let screengrabContainer = document.getElementById("screengrab-container");
    screengrabContainer.appendChild(canvas);
    initDraw(screengrabContainer);

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

function deleteTemplate(event, deleteList=false) {

    if (deleteList) {
        let name = event.target.parentNode.id;
        name = name.split("-");
        let template = name[0];
        let index = name[1] + 1;
        let tableRow = document.getElementById(template + "-table");
        tableRow.deleteCell(index);
        actionTemplateDict[template].splice(index - 1, 1);
    }

    else {
        let currentActionTypeToDeleteNode = event.target.parentNode;
        if (currentActionTypeToDeleteNode.classList[0] === "conditional-action-type") {
            delete actionTemplateDict[currentActionTypeToDeleteNode.innerText];
            actionTemplateDict[currentActionTypeToDeleteNode] = [];
        } else {
            document.getElementById("template-drop-down-contents").removeChild(currentActionTypeToDeleteNode);
            let table = document.getElementById(currentActionTypeToDeleteNode.innerText + "-table");
            table.parentElement.removeChild(table);
            delete actionTemplateDict[currentActionTypeToDeleteNode.innerText];
        }
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
        templateImage.src = "http://i.imgur.com/TWLiACv.png";
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
    if (passedButton === document.getElementById("template-drop-down-button")) {
        document.getElementById("template-drop-down-contents").classList.toggle("show");
    }

    else if (passedButton === document.getElementById("show-templates")) {
        document.getElementById("templates-drop-down-contents").classList.toggle("show");
    }
}

// Heavily inspired by the code from : http://youtubescreenshot.com
// The code on this site is documented nowhere and the source code is somewhat obfuscated.
function decodeStreamMap(decodable) {
    let potentialLinks = {};
    let params = decodable.split(",");
    for (let i = 0; i < params.length; i++) {
        let current_link = decodeQueryString(params[i]);
        let current_type = current_link["type"].split(";")[0];
        let current_quality = current_link["quality"].split(",")[0];
        current_link["original_url"] = current_link["url"];
        current_link["url"] = "" + current_link["url"] + "&signature" + current_link["sig"];
        potentialLinks["" + current_type + " " + current_quality] = current_link;
    }
    return potentialLinks
}

// Heavily inspired by the code from : http://youtubescreenshot.com
// The code on this site is documented nowhere and the source code is heavily obfuscated.
function decodeQueryString(decodeable) {
    let params = decodeable.split("&");
    let keyMap = {};
    for (let i = 0; i < params.length; i++) {
        let keyValues = params[i].split("=");
        let key = decodeURIComponent(keyValues[0]);
        let value = decodeURIComponent(keyValues[1]);
        keyMap[key] = value;
    }
    return keyMap;
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
        $.ajax({
            url: 'https://eywbadb872.execute-api.eu-west-1.amazonaws.com/prod?video_id=' + linkID,
            dataType: "text"
        }).done(function(results) {
            let correctLink;
            let params = decodeQueryString(results);
            let links = decodeStreamMap(params.url_encoded_fmt_stream_map);
            if (links["video/mp4 hd720"] !== undefined) {
                correctLink = links["video/mp4 hd720"]["url"];
            }
            else if (links["video/mp4 medium"] !== undefined) {
                correctLink = links["video/mp4 medium"]["url"];
            }
            else if (links["video/webm medium"] !== undefined) {
                correctLink = links["video/webm medium"];
            }

            let video = document.getElementById("current-video");
            document.getElementById("current-video-source").src = correctLink;
            video.load();
            orgVideoHeight = video.videoHeight;
            orgVideoWidth = video.videoWidth;
            video.style.height = "360px";
            video.style.width = "640px";
        });
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
    data["videoID"] = currentVideo;
    let json = JSON.stringify(data);
    alert("Your video is now being processed! This could take a while.");
    $.ajax({
        // url: 'http://127.0.0.1:5001/api/startedit/',
        url: 'http://127.0.0.1:3000/api/',
        method: 'PUT',
        dataType: 'json',
        data: {
            data: json
        },
        success : function (results) {
            alert(results["link"]);
        },
        error : function(results) {
            if (results.status === 0) {
                alert("The API isn't currently running!");
            }
            else {
                alert("Something went wrong! Make sure you have added action templates!");
                console.log(results);
            }
        },
        timeout: 0
    });
}