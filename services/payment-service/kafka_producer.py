import json
import asyncio
from aiokafka import AIOKafkaProducer
from config import settings

_producer = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await _producer.start()
    return _producer


async def publish(topic: str, message: dict):
    try:
        producer = await get_producer()
        await producer.send_and_wait(topic, message)
    except Exception as e:
        print(f"[Kafka] Publish error on topic '{topic}': {e}")


async def stop_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
