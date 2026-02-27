import threading
import traceback
import xml.etree.ElementTree as ET
from confluent_kafka import Consumer, KafkaError
from .db import SessionLocal
from .models import Message

def parse_cot_xml(raw):
    try:
        root = ET.fromstring(raw)
        event = root if root.tag == 'event' else root.find('.//event') or root
        uid = event.get('uid') or ''
        typ = event.get('type') or ''
        how = event.get('how') or ''
        time_attr = event.get('time') or ''
        point = event.find('.//point')
        lat = float(point.get('lat')) if point is not None and point.get('lat') else None
        lon = float(point.get('lon')) if point is not None and point.get('lon') else None
        return dict(uid=uid, type=typ, how=how, time=time_attr, lat=lat, lon=lon)
    except Exception:
        return dict(uid='', type='', how='', time='', lat=None, lon=None)

def start_consumer(broker='localhost:9092', topic='cot', group_id='cot-receiver'):
    def _run():
        conf = {'bootstrap.servers': broker, 'group.id': group_id, 'auto.offset.reset': 'earliest'}
        c = Consumer(conf)
        c.subscribe([topic])
        try:
            while True:
                msg = c.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        continue
                raw = msg.value().decode('utf-8', errors='replace')
                parsed = parse_cot_xml(raw)
                session = SessionLocal()
                try:
                    m = Message(uid=parsed['uid'], type=parsed['type'], how=parsed['how'],
                                time=parsed['time'], lat=parsed['lat'], lon=parsed['lon'],
                                raw_xml=raw)
                    session.add(m)
                    session.commit()
                except Exception:
                    session.rollback()
                    traceback.print_exc()
                finally:
                    session.close()
        except Exception:
            traceback.print_exc()
        finally:
            c.close()
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t