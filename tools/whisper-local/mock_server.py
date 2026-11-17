"""A stand-in for the StreamRemaster server that only answers the control messages (models), with
the server's own code (server/whisper_live/st_models.py). For trying the extension's settings and
popup without loading Whisper. Works with the asyncio API of websockets 10 (Linux Mint's).

Usage: python3 mock_server.py <st_models.py> <video models dir> [port]
"""
import asyncio
import importlib.util
import json
import os
import sys

import websockets

spec = importlib.util.spec_from_file_location("st_models", sys.argv[1])
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
M.VIDEO_DIR = os.path.abspath(sys.argv[2])
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 9095


class Reply:
    """What handle_control sends, kept to be sent from the event loop."""
    def __init__(self):
        self.text = None

    def send(self, text):
        self.text = text


async def handle(websocket, path=None):
    options = json.loads(await websocket.recv())
    if options.get("st_action") == "list_models":
        await websocket.send(json.dumps({"ok": True, "models": [], "jobs": [], "default": None, "loaded": None,
                                         "st": M.PROTOCOL_VERSION, "version": M.SERVER_VERSION, "management": True}))
        return
    reply = Reply()
    # downloads block: off the event loop
    await asyncio.get_running_loop().run_in_executor(None, M.handle_control, reply, options, "")
    if reply.text:
        await websocket.send(reply.text)


async def main():
    async with websockets.serve(handle, "127.0.0.1", PORT, max_size=None):
        print("listening on", PORT, flush=True)
        await asyncio.Future()


asyncio.run(main())
