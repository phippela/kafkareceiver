import asyncio
import uuid
import time
import aio_pika

AMQP_URL = "amqp://guest:guest@localhost:5673/"
QUEUE = "cot"


def make_cot(uid=None, lat=60.182664, lon=24.952986, callsign="TEST1"):
    uid = uid or str(uuid.uuid4())
    t = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    stale = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 30 * 86400))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<event version="2.0" uid="{uid}" type="a-f-G-U-C-A" '
        f'time="{t}" start="{t}" stale="{stale}" how="h-g-i-g-o">\n'
        f'    <point lat="{lat}" lon="{lon}" hae="0.0" ce="1.0" le="1.0"/>\n'
        f'    <detail>\n'
        f'        <contact callsign="{callsign}"/>\n'
        f'        <link point="{lat},{lon}"/>\n'
        f'    </detail>\n'
        '</event>\n'
    )


async def main():
    connection = await aio_pika.connect_robust(AMQP_URL)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE, durable=True)
        body = make_cot().encode()
        await channel.default_exchange.publish(
            aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=QUEUE,
        )
        print(f"Sent sample CoT to queue '{QUEUE}'")

asyncio.run(main())