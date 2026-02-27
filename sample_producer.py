from confluent_kafka import Producer
import time
import uuid

def make_cot(uid=None, lat=60.1699, lon=24.9384):
    uid = uid or str(uuid.uuid4())
    t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    return f'''<event uid="{uid}" type="a-f-G-UAS" how="m-g" time="{t}">
  <point lat="{lat}" lon="{lon}" hae="0" ce="999999" le="999999"/>
  <detail>
    <contact callsign="TEST"/>
  </detail>
</event>'''

if __name__ == '__main__':
    p = Producer({'bootstrap.servers':'localhost:9092'})
    msg = make_cot()
    p.produce('cot', value=msg.encode('utf-8'))
    p.flush()
    print('sent sample cot message')