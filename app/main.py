from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from .db import engine, SessionLocal, Base
from .models import Message
from .amqp_consumer import start_consumer

AMQP_URL = "amqp://guest:guest@localhost/"
AMQP_QUEUE = "cot"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_consumer(url=AMQP_URL, queue_name=AMQP_QUEUE)
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    db = next(get_db())
    msgs = db.query(Message).order_by(Message.received_at.desc()).limit(100).all()
    return templates.TemplateResponse("index.html", {"request": request, "messages": msgs})


@app.get("/message/{msg_id}", response_class=HTMLResponse)
def message_detail(request: Request, msg_id: int):
    db = next(get_db())
    m = db.query(Message).get(msg_id)
    if not m:
        raise HTTPException(status_code=404, detail="Message not found")
    return templates.TemplateResponse("detail.html", {"request": request, "msg": m})


@app.post("/message/{msg_id}/delete")
def delete_message(msg_id: int):
    db = next(get_db())
    m = db.query(Message).get(msg_id)
    if not m:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(m)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/messages")
def api_messages():
    db = next(get_db())
    msgs = db.query(Message).order_by(Message.received_at.desc()).limit(1000).all()
    return [{"id": m.id, "uid": m.uid, "type": m.type, "time": m.time, "lat": m.lat, "lon": m.lon} for m in msgs]