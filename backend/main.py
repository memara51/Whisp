from fastapi import FastAPI
from rooms import generate_room_id
from rooms import rooms
from fastapi import WebSocket, WebSocketDisconnect
app=FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World!" }


@app.get("/status")
async def status():
    return "Whisp server is running"


@app.post("/api/rooms")
async def create_room():
    room_id=generate_room_id()
    rooms[room_id]=[]
    return {"room_id":room_id}


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):

    if room_id in rooms:

        if len(rooms[room_id]) < 2:
            await websocket.accept()

            rooms[room_id].append(websocket)

            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Server received: {data}")

            except WebSocketDisconnect:
                print("Client disconnected")

                connections = rooms.pop(room_id, [])

                for connection in connections:
                    if connection is not websocket:
                        await connection.close(
                            code=1000,
                            reason="Chat session ended"
                        )

        else:
            await websocket.close(
                code=1008,
                reason="Maximum users reached"
            )

    else:
        await websocket.close(
            code=1008,
            reason="Room does not exist"
        )