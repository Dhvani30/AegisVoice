import asyncio
import websockets
import json

async def listen():
    uri = "ws://127.0.0.1:8765"
    async with websockets.connect(uri) as websocket:
        print("Fake UI Connected. Listening for scam alerts...\n")
        while True:
            message = await websocket.recv()
            print(f"INCOMING UI ALERT: {json.loads(message)}")

asyncio.run(listen())