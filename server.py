"""Server to log each JSON to a single randomly named file"""
import os
import json
import uuid

from aiohttp import web
import aiohttp_cors

if not os.path.exists('logged'):
    os.makedirs('logged')
    print('I created the logged folder')


async def handle_track(request):
    """Save the request JSON in a new file."""
    data = await request.json()
    print(data['location'])
    with open('logged/' + str(uuid.uuid4()), 'w') as f:
        f.write(json.dumps(data))
    return web.Response(text='done')

app = web.Application()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})
resource = cors.add(app.router.add_resource("/log_visit"))
cors.add(resource.add_route("POST", handle_track))

web.run_app(app, port=8987)
