from channels.staticfiles import StaticFilesConsumer
from . import consumers


# There's no path matching on these routes; we just rely on the matching
# from the top-level routing. We _could_ path match here if we wanted.
channel_routing = {
    'http.request': StaticFilesConsumer(),

    # Called when WebSockets connect
    'websocket.connect': consumers.ws_connect,

    # Called when WebSockets get sent a data frame
    'websocket.receive': consumers.ws_receive,

    # Called when WebSockets disconnect
    'websocket.disconnect': consumers.ws_disconnect,
}
