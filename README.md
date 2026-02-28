# CoT-XML Kafka Receiver

A FastAPI application that consumes CoT-XML (Cursor on Target) messages from a Kafka topic, stores them in a local SQLite database, and displays them in a web browser — including an OpenStreetMap view of each message's coordinates.

---

## Requirements

- Ubuntu 24.04
- Docker & Docker Compose
- Python 3.12+

---

## 1. Python Environment Setup (Ubuntu 24.04)

Ubuntu 24.04 ships with Python 3.12 but restricts system-wide `pip` installs. Use a virtual environment.

```bash
# Install system dependencies required by confluent-kafka
sudo apt update
sudo apt install -y python3-dev python3-venv python3-pip librdkafka-dev

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

> The virtual environment must be activated (`source .venv/bin/activate`) every time you open a new terminal before running the app or producer.

---

## 2. Start Kafka with Docker Compose

A `docker-compose.yml` is included that runs Zookeeper and a single-node Kafka broker (Confluent Platform 7.4.1).

```bash
docker compose up -d
```

This exposes Kafka on `localhost:9092`.

To check that the broker is up:

```bash
docker compose ps
docker compose logs kafka
```

To stop Kafka:

```bash
docker compose down
```

---

## 3. Start the FastAPI Server

Make sure the virtual environment is active and Kafka is running, then:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

The server will start at **http://localhost:8000**.

- **Message list with map:** http://localhost:8000/
- **Message detail:** http://localhost:8000/message/{id}

---

## 4. Send Test Messages

With the virtual environment active and the server running, open a second terminal and send a sample CoT-XML message:

```bash
source .venv/bin/activate
python sample_producer.py
```

The producer sends a single CoT event (default coordinates: Helsinki, Finland) to the `cot` topic. Refresh the browser to see the new entry.

To customise the broker, topic, or coordinates, edit `sample_producer.py`.

---

## 5. Web GUI

| Feature | Description |
|---|---|
| Message list | Main page shows UID, type, timestamp and a map of all received positions |
| Message detail | Click **open** on any row to see the full raw XML and a single-point map |
| Delete | Click **delete** on the list row or the detail page to permanently remove an entry |

---

## Defaults

| Setting | Value |
|---|---|
| Kafka broker | `localhost:9092` |
| Kafka topic | `cot` |
| Consumer group | `cot-receiver` |
| Database | `data.db` (SQLite, auto-created on first run) |
| Web server | `http://localhost:8000` |