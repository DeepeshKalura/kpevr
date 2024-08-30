from typing import Annotated, Any, Dict, List
from fastapi import FastAPI, Form, Request, Response, WebSocket, WebSocketDisconnect 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2.utils import htmlsafe_json_dumps
from pydantic import BaseModel
app = FastAPI()

origins = ["*"]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define template

template = Jinja2Templates(directory="template")

@app.get("/")
def read_root(request: Request):
    return template.TemplateResponse(
            request=request,
            name="index.html",
            context={}
    )


@app.get("/lobby")
def read_room(request: Request):
    return template.TemplateResponse(
            request=request,
            name="lobby.html",
            context={}
    )

@app.post("/", status_code=200)
def create_user(response: Response, user_id: str = Form(...), email: str= Form(...), room_id: str= Form(...)):
    # with open(f"{room_id}.txt", "a+") as f:
      #  f.write(f"user_id: {user_id}\n")
       # f.write(f"email: {email}\n")
        #f.write("\n")
        #f.close()
    # cookies  <-- store on the  front-end all the information and later i will use them for the sending offer and answer to the peer connection makes sense

    response.set_cookie(key="user_id", value=user_id)
    response.set_cookie(key="email", value=email)

    # return RedirectResponse(
        # Wrong method a better way of manangement can be there 
        #url=f"http://127.0.0.1:8000/rooms/{room_id}",
        #status_code=302,
    #)
    # The method was bad because we cannot getting the request done

    return  {
        "success" : "true"
    }

# Created a model mapping email --> to json@app.get("/rooms/{id}", response_class=HTMLResponse)
@app.get("/rooms/{room_id}", response_class=HTMLResponse)
async def rooms_html(request: Request, room_id:str):
    return  template.TemplateResponse(
            request=request,
            name="room.html",
            context={room_id: room_id}, 
    )


peer_connections:Dict[ WebSocket, int] = {}


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connection:List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, id:int):
            await websocket.accept()
            peer_connections[websocket] = id
            self.active_connection.append(websocket)

    def disconnect(self, websocket:WebSocket):
            if websocket:
                self.active_connection.remove(websocket)
                del peer_connections[websocket]
    async def broadcast(self, data:Dict, websocket:WebSocket):
        for connection in self.active_connection:
            if(connection != websocket):
                await connection.send_json(data)

manager = ConnectionManager()
# signnal server
@app.websocket("/ws")
async def signaling_server(websocket: WebSocket):
    unique_id = id(websocket)
    await manager.connect(websocket, unique_id)
    while True:
        try: 
            gettingOffer:Dict = await websocket.receive_json() 
            print(gettingOffer)
            await manager.broadcast(data=gettingOffer, websocket=websocket)
            print(manager.active_connection)
            print("I think all done")
            # if you get the offer then you have to brocast it to other user
            # the others user will either accept or reject but we will only going to accept it 
            # so others user just accept my call then i think so the web_rtc should get implement then we just have send streams 


        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
