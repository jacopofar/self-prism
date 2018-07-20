setTimeout(() => {
    const totalBody = new XMLSerializer().serializeToString(document);

    const msg = JSON.stringify({
        location: location.href,
        title: document.title,
        referrer: document.referrer,
        ts: new Date().toISOString(),
        content: totalBody
    });
    console.log('sending message of length:', msg.length);
    browser.runtime.sendMessage(msg);
    console.log(' +++ page content logged +++');
}, 3000);
