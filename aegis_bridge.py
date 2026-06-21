import asyncio
import websockets
import json
import threading
import logging

class AegisBridge:
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None

    async def handler(self, websocket):
        """Handles a new UI client connecting."""
        self.clients.add(websocket)
        logging.info(f" UI Client connected! (Total: {len(self.clients)})")
        try:
            async for _ in websocket:
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logging.info(f" UI Client disconnected. (Total: {len(self.clients)})")

    async def broadcast(self, message_dict):
        """Sends the alert to all connected UI clients."""
        if self.clients:
            message = json.dumps(message_dict)
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    def start_server(self):
        """Starts the WebSocket server in a background thread."""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            async def main():
                async with websockets.serve(self.handler, self.host, self.port):
                    logging.info(f"Aegis Bridge active. Waiting for UI on ws://{self.host}:{self.port}")
                    await asyncio.Future()  # run forever
            
            self.loop.run_until_complete(main())

        server_thread = threading.Thread(target=run_loop, daemon=True)
        server_thread.start()

    def send_alert(self, alert_data):
        """Thread-safe method to send data from the audio engine to the websocket loop."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast(alert_data), self.loop)