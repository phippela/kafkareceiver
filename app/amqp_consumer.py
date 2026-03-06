import asyncio
import traceback
import xml.etree.ElementTree as ET
import aio_pika
from .db import SessionLocal
from .models import Message


def strip_amqp_prefix(data: bytes) -> str:
    """Strip the 8-byte AMQP 1.0 data-section header if present, return UTF-8 string."""
    idx = data.find(b"<")
    if idx > 0:
        data = data[idx:]
    return data.decode("utf-8", errors="replace")


def parse_cot_xml(raw: str) -> dict:
    try:
        root = ET.fromstring(raw)
        event = root if root.tag == "event" else (root.find(".//event") or root)
        uid         = event.get("uid") or ""
        version     = event.get("version") or ""
        typ         = event.get("type") or ""
        how         = event.get("how") or ""
        time_attr   = event.get("time") or ""
        event_start = event.get("start") or ""
        stale       = event.get("stale") or ""
        point = event.find(".//point")
        lat = float(point.get("lat")) if point is not None and point.get("lat") else None
        lon = float(point.get("lon")) if point is not None and point.get("lon") else None
        hae = float(point.get("hae")) if point is not None and point.get("hae") else None
        ce  = float(point.get("ce"))  if point is not None and point.get("ce")  else None
        le  = float(point.get("le"))  if point is not None and point.get("le")  else None
        contact  = event.find(".//detail/contact")
        callsign = contact.get("callsign") if contact is not None else ""
        return dict(uid=uid, version=version, type=typ, how=how, time=time_attr,
                    event_start=event_start, stale=stale,
                    lat=lat, lon=lon, hae=hae, ce=ce, le=le, callsign=callsign)
    except Exception:
        traceback.print_exc()
        return dict(uid="", version="", type="", how="", time="",
                    event_start="", stale="", lat=None, lon=None,
                    hae=None, ce=None, le=None, callsign="")


async def _consume_loop(url: str, queue_name: str) -> None:
    while True:
        try:
            connection = await aio_pika.connect_robust(url)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                queue = await channel.declare_queue(queue_name, durable=False)
                print(f"[AMQP] Listening on queue '{queue_name}' at {url}")
                async with queue.iterator() as it:
                    async for message in it:
                        async with message.process():
                            raw = strip_amqp_prefix(message.body)
                            parsed = parse_cot_xml(raw)
                            session = SessionLocal()
                            try:
                                m = Message(
                                    uid=parsed["uid"],
                                    version=parsed["version"],
                                    type=parsed["type"],
                                    how=parsed["how"],
                                    time=parsed["time"],
                                    event_start=parsed["event_start"],
                                    stale=parsed["stale"],
                                    lat=parsed["lat"],
                                    lon=parsed["lon"],
                                    hae=parsed["hae"],
                                    ce=parsed["ce"],
                                    le=parsed["le"],
                                    callsign=parsed["callsign"],
                                    raw_xml=raw,
                                )
                                session.add(m)
                                session.commit()
                                print(f"[AMQP] stored uid={parsed['uid']} callsign={parsed['callsign']}")
                            except Exception:
                                session.rollback()
                                traceback.print_exc()
                            finally:
                                session.close()
        except Exception:
            traceback.print_exc()
            print("[AMQP] Connection lost, retrying in 5 s ...")
            await asyncio.sleep(5)


def start_consumer(url: str = "amqp://guest:guest@localhost/", queue_name: str = "cot") -> None:
    asyncio.create_task(_consume_loop(url, queue_name))