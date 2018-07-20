'use strict';
const notifyF = function(message) {
    console.log("background script received message");
    console.log(message.substr(0, 300));



    fetch('http://localhost:8987/log_visit', {
    method: 'POST', // or 'PUT'
    body: message, // data can be `string` or {object}!
    headers:{
        'Content-Type': 'application/json'
    }
});
};

chrome.runtime.onMessage.addListener(notifyF);
