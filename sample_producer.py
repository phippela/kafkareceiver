import asyncio
import uuid
import time
import aio_pika

AMQP_URL = "amqp://guest:guest@localhost/"
QUEUE = "cot"


def make_cot(uid=None, lat=60.1699, lon=24.9384):
    uid = uid or str(uuid.uuid4())
    t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return f'''<event uid="{uid}" type="a-f-G-UAS" how="m-g" time="{t}">
  <point lat="{lat}" lon="{lon}" hae="0" ce="999999" le="999999"/>
  <detail><contact callsign="TEST"/></detail>
</event>'''


async def main():
    connection = await aio_pika.connect_robust(AMQP_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE, durable=True)
        body = make_cot().encode()
        await channel.default_exchange.publish(
            aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=QUEUE,
        )
        print(f"Sent sample CoT message to queue '{QUEUE}'")

asyncio.run(main())