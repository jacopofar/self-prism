const totalBody = new XMLSerializer().serializeToString(document);

const msg = JSON.stringify({
    location: location.href,
    title: document.title,
    referrer: document.referrer,
    ts: new Date().toISOString(),
    content: totalBody
});
console.log(msg);

setTimeout(() => {
chrome.runtime.sendMessage(msg);
console.log('MESSAGE SENT');
}, 3000);

