# Self PRISM

_Spy yourself!_

This tool lets you store the rendered HTML of each page you visit in a file, incuding the URL, title and timestamp.

The two browser extensions (for chrome and firefox) send the data as a JSON to a server listening at `localhost:8987`. Firefox one also lets you toggle it on and off.

`server.py` is a server which saves the data. It requires `aiohttp` and Python 3.5 or greater.

No tests, no docs, take as is. Free as in free beer and free speech.