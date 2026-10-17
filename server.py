import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in list(self.active):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                self.disconnect(ws)

manager = ConnectionManager()

@app.get("/")
def root():
    return {"status": "Chat server running", "clients": len(manager.active)}

@app.websocket("/ws/{username}")
async def chat(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await manager.broadcast({"user": "System", "text": f"{username} joined"})
    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast({"user": username, "text": text})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"user": "System", "text": f"{username} left"})