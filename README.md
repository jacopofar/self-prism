# Self PRISM

_Spy yourself!_

This tool lets you store the rendered HTML of each page you visit in a file, incuding the URL, title and timestamp.

~~The two browser extensions (for chrome and firefox) send the data as a JSON to a server listening at `localhost:8987`. Firefox one also lets you toggle it on and off.~~
Apparently creating and publishing a Firefox extension is a pain (it has to be approved by Mozilla each time, currently waiting).

Use the `tampermonkey.js` script in this repository. It will be injected in each visited page.

`server.py` is a server which saves the data.

Some tests, no docs, take as is. Free as in free beer and free speech.

## How to run

Ok, there's *some* documentation after all. All the commands are in the Makefile, which is quite self-explanatory. The extension only takes care to send the page content (with some adaptation) and the context to the server, which stores it in a local SQLLite database.


## Running the server at startup

On a Linux machine you can set up a script for systemd like this one:

```bash
#!/usr/bin/bash
# this is to get UV in the PATH
source /home/yourname/.bashrc
cd /home/yourname/yourfolder/self-prism
make run_dev
```

and then a systemd unit like this under `~/.config/systemd/user/selfprism.service`:

to be enabled with `systemctl --user enable selfprism.service`

```
[Unit]
Description=Run selfprism server

[Service]
Type=simple
ExecStart=/home/yourname/startprism.sh
Restart=on-failure

[Install]
WantedBy=default.target
```
