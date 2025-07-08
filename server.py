import asyncio
import websockets
import json

clients = {}

async def handler(websocket, path):
    client_id = path.strip("/").split("/")[-1]  # A or B
    clients[client_id] = websocket
    print(f"[INFO] {client_id} connected")

    try:
        async for message in websocket:
            print(f"[RECV] {client_id}: {message}")
            for target_id, target_ws in clients.items():
                if target_ws.open:
                    await target_ws.send(json.dumps({
                        "from": client_id,
                        "gesture": message
                    }))
    except websockets.exceptions.ConnectionClosed:
        print(f"[INFO] {client_id} disconnected")
        clients.pop(client_id, None)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("WebSocket server running on port 10000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
