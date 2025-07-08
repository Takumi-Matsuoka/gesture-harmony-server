import asyncio
import json
import websockets

clients = {}

# ──────────────────────────────────────────
# ① ここが追加ポイント
async def process_request(path, request_headers):
    """Upgrade ヘッダが無い (普通の HTTP) ときは 200 OK を返す"""
    if request_headers.get("Upgrade", "").lower() != "websocket":
        return (
            200,                          # status
            [("Content-Type", "text/plain")],  # headers
            b"OK\n"                       # body
        )
    # WebSocket Upgrade のときは None を返して通常ハンドシェイクへ
    return None
# ──────────────────────────────────────────

async def handler(websocket, path):
    client_id = path.strip("/").split("/")[-1]  # "A" または "B"
    clients[client_id] = websocket
    print(f"[INFO] {client_id} connected")

    try:
        async for message in websocket:
            print(f"[RECV] {client_id}: {message}")
            # そのまま全クライアントへブロードキャスト
            for _, ws in list(clients.items()):
                if ws.open:
                    await ws.send(json.dumps({"from": client_id, "gesture": message}))
    except websockets.exceptions.ConnectionClosed:
        print(f"[INFO] {client_id} disconnected")
    finally:
        clients.pop(client_id, None)

async def main():
    # ② process_request を渡す
    async with websockets.serve(
        handler,
        "0.0.0.0",
        10000,
        process_request=process_request    # ← 追加
    ):
        print("WebSocket server running on port 10000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
