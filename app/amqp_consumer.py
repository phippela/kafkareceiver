import asyncio
import traceback
import xml.etree.ElementTree as ET
import aio_pika
from .db import SessionLocal
from .models import Message


def parse_cot_xml(raw: str) -> dict:
    try:
        root = ET.fromstring(raw)
        event = root if root.tag == "event" else (root.find(".//event") or root)
        uid = event.get("uid") or ""
        typ = event.get("type") or ""
        how = event.get("how") or ""
        time_attr = event.get("time") or ""
        point = event.find(".//point")
        lat = float(point.get("lat")) if point is not None and point.get("lat") else None
        lon = float(point.get("lon")) if point is not None and point.get("lon") else None
        return dict(uid=uid, type=typ, how=how, time=time_attr, lat=lat, lon=lon)
    except Exception:
        return dict(uid="", type="", how="", time="", lat=None, lon=None)


async def _consume_loop(url: str, queue_name: str) -> None:
    while True:
        try:
            connection = await aio_pika.connect_robust(url)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                queue = await channel.declare_queue(queue_name, durable=True)
                print(f"[AMQP] Listening on queue '{queue_name}' at {url}")
                async with queue.iterator() as it:
                    async for message in it:
                        async with message.process():
                            raw = message.body.decode("utf-8", errors="replace")
                            parsed = parse_cot_xml(raw)
                            session = SessionLocal()
                            try:
                                m = Message(
                                    uid=parsed["uid"],
                                    type=parsed["type"],
                                    how=parsed["how"],
                                    time=parsed["time"],
                                    lat=parsed["lat"],
                                    lon=parsed["lon"],
                                    raw_xml=raw,
                                )
                                session.add(m)
                                session.commit()
                                print(f"[AMQP] stored uid={parsed['uid']}")
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
    """Schedule the AMQP consumer as a background asyncio task."""
    asyncio.create_task(_consume_loop(url, queue_name))