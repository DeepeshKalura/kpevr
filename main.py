from fastapi import FastAPI, Request, websockets
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket

app = FastAPI()

origins = ["http://127.0.0.0"]



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
            name="root.html",
            context={}
    )

@app.websocket("/ws")
async def signaling_server(websocket :  WebSocket):
    await websocket.accept()

    while True:
        pass
