/**
 * @param {CSSStyleSheet} sheet
 */
async function serializeSheet(sheet) {
  if (sheet.disabled) {
    return "";
  }

  if (sheet.cssRules == null && sheet.href != null) {
    // can be null because of cross origin policy
    const res = await fetch(sheet.href); // works nicely because it hits the cache
    if (res.ok) {
      const style = await res.text();
      return "<style>\n" + style + "\n</style>\n";
    } else {
      throw new Error(`Failed to load ${sheet}`);
    }
  }

  let cssrules = "<style>";
  for (rule of sheet.cssRules) {
    cssrules += rule.cssText;
  }
  cssrules += "</style>";
  return cssrules;
}
async function serializeStyles() {
  let cssrules = "";
  const sheets = document.styleSheets;
  for (const sheet of sheets) {
    try {
      cssrules += await serializeSheet(sheet);
    } catch (error) {
      console.log(error);
    }
  }
  return cssrules;
}

async function serializeHTML() {
  let html = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8" />
  `;
  html += await serializeStyles();
  html += `</head>`;
  html += new XMLSerializer().serializeToString(document.body);
  html += `</html>`;
  return html;
}

function getDescription() {
  return (
    document.querySelector('meta[name="twitter:description"]')?.content ??
    document.querySelector('meta[name="og:description"]')?.content ??
    document.querySelector('meta[name="description"]')?.content ??
    null
  );
}

async function postVisit() {
  const msg = JSON.stringify({
    url: location.href,
    title: document.title,
    description: getDescription(),
    referrer: document.referrer,
    content_html: await serializeHTML(),
  });
  console.log("sending message of length:", msg.length);
  browser.runtime.sendMessage(msg);
  console.log(" +++ page content logged +++");
}

/**
 * The values in this set are checked against `new URL(href).host` to determine
 * whether or not a page should be logged.
 *
 * I think search engines should be ignored because they pollute semantic search
 * and they're not really "visited" pages you'll want to go back to.
 *
 * I think messaging apps should be ignored as they can leak private information
 * and are very dynamic in nature so there's no point going back in time to a URL.
 */
const IGNORE_HOSTS = new Set([
  // search engines
  "google.com",
  "bing.com",
  "duckduckgo.com",
  "yandex.com",
  // messaging
  "app.slack.com",
  "teams.microsoft.com",
  "web.whatsapp.com",
  "web.telegram.org",
]);

/**
 * The values in this set are checked against `new URL(href).hostname` to determine
 * whether or not a page should be logged.
 */
const IGNORE_HOSTNAMES = new Set([
  "localhost",
  "127.0.0.1",
]);

/**
 * This value controls how much time needs to be spent on a page before it's
 * logged. A higher number will probably yield better results:
 * - dynamic content on the page might not be immediately available on page load
 * - if you close a page right away, you most likely don't want to store a copy of it
 */
const LOG_DELAY = 3000;

/**
 * @param {string} urlString
 */
function shouldIgnoreURL(urlString) {
  const url = new URL(urlString);
  return IGNORE_HOSTNAMES.has(url.hostname) || IGNORE_HOSTS.has(url.host);
}

function observeUrlChange() {
  let oldHref = document.location.href;
  const body = document.querySelector("body");
  const observer = new MutationObserver((mutations) => {
    if (oldHref !== document.location.href) {
      oldHref = document.location.href;
      if (!shouldIgnoreURL(location.href)) {
        setTimeout(postVisit, LOG_DELAY);
      }
    }
  });
  observer.observe(body, { childList: true, subtree: true });
}

window.onload = observeUrlChange;

if (!shouldIgnoreURL(location.href)) {
  setTimeout(postVisit, LOG_DELAY);
}
