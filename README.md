# Self PRISM

_Spy yourself!_

This tool lets you store the rendered HTML of each page you visit in a file, incuding the URL, title and timestamp.

The two browser extensions (for chrome and firefox) send the data as a JSON to a server listening at `localhost:8987`. Firefox one also lets you toggle it on and off.

`server.py` is a server which saves the data.

Some tests, no docs, take as is. Free as in free beer and free speech.

## How to run

Ok, there's *some* documentation after all. All the commands are in the Makefile, which is quite self-explanatory. The extension only takes care to send the page content (with some adaptation) and the context to the server, which stores it in a local SQLLite database.
