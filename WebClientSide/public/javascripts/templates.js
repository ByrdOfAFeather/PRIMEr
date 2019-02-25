let currentTemplateType = null;
let currentVideo = null;
let actionTemplateDict = {};
let conditionals = {};
let currentTime = null;
let templatesShowing = false;
let templateTable = document.getElementById("template-table");
let videoID = "";

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
    console.log(rectangleX - position["left"]);
    console.log(rectangleY);
    ctx.drawImage(v, rectangleX - position["left"], rectangleY - position["top"], rectangleWidth , rectangleHeight, 0, 0, rectangleWidth, rectangleHeight);

    if (!currentTemplateType) { alert("Please selection an action type before saving an action!"); }

    if (document.getElementById(currentTemplateType.toLowerCase()).classList[0] === "conditional-action-type") {
        conditionals[currentTemplateType] = [];
        conditionals[currentTemplateType].push(currentTime);
    }

    else {
        try {
            actionTemplateDict[currentTemplateType].push("NONE");
        }
        catch (TypeError) {
            actionTemplateDict[currentTemplateType] = [];
            actionTemplateDict[currentTemplateType].push("NONE");
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

function grabScreen() {
    let video = document.getElementById('current-video');

    let videoHeight = video.videoHeight;
    let videoWidth = video.videoWidth;

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

function displayNewVideo(link) {
    // TODO: API CALL?
}

function loadVideo() {
    console.log("I got here");
    let input = document.getElementById("input-video");
    let link = input.value;
    if (link.slice(0, 32) !== "https://www.youtube.com/watch?v=") {
        alert("Please input a valid Youtube URL!")
    }
    else {
        let linkID = link.slice(32);
        currentVideo = linkID;
        console.log(linkID);
        $.ajax({
            url: 'https://eywbadb872.execute-api.eu-west-1.amazonaws.com/prod?video_id=' + linkID,
            method: 'get',
            success : function (results) {
                // This never happens as the query is treated as a failure
            },
            error : function(results) {
                if (results.status === 0) {
                    alert("Somehow the server isn't running?");
                }
                else {
                    let potentialLinks = results.responseText;
                    console.log(potentialLinks);
                    potentialLinks = potentialLinks.split("https");
                    console.log(potentialLinks);
                    let newPotentialLinks = [];
                    for (let i = 0; i < potentialLinks.length; i++) {
                        let links = potentialLinks[i];
                        links = decodeURIComponent(links);
                        console.log(links);
                        console.log(links.includes("mime=video"));
                        if (links.includes("mime=video%2Fmp4")) {
                            let addedLinkArray = links.split(("\""));
                            let addedLink = addedLinkArray[0];
                            addedLink = addedLink.replace(/\\u[\dA-F]{4}/gi,
                                function (match) {
                                    return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
                                });
                            addedLink = "https" + addedLink;
                            newPotentialLinks.push(addedLink);
                        }
                    }
                    document.getElementById("current-video").load();
                    document.getElementById("current-video-source").src = newPotentialLinks[0];
                    console.log(newPotentialLinks);
                }
            }
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