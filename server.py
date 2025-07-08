import json
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import uvicorn

app = FastAPI()
clients: Dict[str, WebSocket] = {}

# ----- Render の Health Check 用 -----
@app.get("/")
async def root_get():
    return PlainTextResponse("OK")

@app.head("/")
async def root_head():
    return PlainTextResponse("OK")

# ----- WebSocket (/ws/A, /ws/B) -----
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: str):
    await ws.accept()
    clients[client_id] = ws
    print(f"[INFO] {client_id} connected")

    try:
        while True:
            msg = await ws.receive_text()
            print(f"[RECV] {client_id}: {msg}")
            # ブロードキャスト
            for _, other in list(clients.items()):
                if other.client_state.name == "CONNECTED":
                    await other.send_text(json.dumps({"from": client_id,
                                                      "gesture": msg}))
    except WebSocketDisconnect:
        print(f"[INFO] {client_id} disconnected")
    finally:
        clients.pop(client_id, None)

# ----- エントリーポイント（ローカル実行も可） -----
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=10000)
