Simple Cot-XML Kafka receiver (FastAPI + confluent-kafka)

Install:
pip install -r requirements.txt

Run the app:
uvicorn app.main:app --reload

Defaults:
- Kafka broker: localhost:9092
- Topic: cot

Test producer:
python sample_producer.py
(Adjust broker/ topic if needed)

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# start FastAPI
uvicorn app.main:app --reload
# in another terminal send sample message:
python sample_producer.py