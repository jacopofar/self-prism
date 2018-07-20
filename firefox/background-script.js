'use strict';
let isActive = true;

const notifyF = function(message) {
    if(!isActive){
        console.log('not active, ignoring request to log');
        return;
    }
    console.log("logging the visited page content");
    console.log(message.substr(0, 300));



    fetch('http://localhost:8987/log_visit', {
    method: 'POST',
    body: message,
    headers:{
        'Content-Type': 'application/json'
    }
});
};

browser.runtime.onMessage.addListener(notifyF);

function toggleState() {
    console.log('button clicked, toggling');
    if(isActive){
        browser.browserAction.setIcon({path: "icons/border-disable-48.png"});
        browser.browserAction.setTitle({title: "Selfprism, not registering"})
    }
    else {
        browser.browserAction.setIcon({path: "icons/border-48.png"});
        browser.browserAction.setTitle({title: "Selfprism, registering all pages content"})
    }
    isActive = !isActive;
}

browser.browserAction.onClicked.addListener(toggleState);