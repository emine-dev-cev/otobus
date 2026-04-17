import json
import asyncio
from aiokafka import AIOKafkaConsumer
from config import settings
from database import SessionLocal
from models import Notification, NotificationType, NotificationStatus


TOPICS = ["booking.created", "booking.cancelled", "payment.success", "payment.failed"]


async def handle_event(topic: str, data: dict):
    db = SessionLocal()
    try:
        subject = ""
        body = ""
        user_id = data.get("user_id", "")

        if topic == "booking.created":
            subject = "✅ Rezervasyonunuz Oluşturuldu"
            body = (
                f"Sayın yolcu, rezervasyonunuz başarıyla oluşturuldu.\n"
                f"Rezervasyon No: {data.get('booking_id')}\n"
                f"Koltuk: {data.get('seat_number')}\n"
                f"Toplam Tutar: {data.get('total_price')} TL\n\n"
                f"Ödemenizi tamamlamak için ödeme sayfasına gidiniz."
            )
        elif topic == "booking.cancelled":
            subject = "❌ Rezervasyonunuz İptal Edildi"
            body = (
                f"Rezervasyonunuz iptal edildi.\n"
                f"Rezervasyon No: {data.get('booking_id')}\n"
                f"Koltuk: {data.get('seat_number')}"
            )
        elif topic == "payment.success":
            subject = "💳 Ödemeniz Alındı"
            body = (
                f"Ödemeniz başarıyla alındı.\n"
                f"İşlem Kodu: {data.get('transaction_id')}\n"
                f"Tutar: {data.get('amount')} TL\n\n"
                f"İyi yolculuklar dileriz! 🚌"
            )
        elif topic == "payment.failed":
            subject = "⚠️ Ödeme Başarısız"
            body = (
                f"Ödeme işleminiz gerçekleştirilemedi.\n"
                f"Rezervasyon No: {data.get('booking_id')}\n"
                f"Lütfen tekrar deneyiniz."
            )

        notification = Notification(
            user_id=user_id,
            type=NotificationType.email,
            subject=subject,
            body=body,
            status=NotificationStatus.sent,   # Mock: assume always sent
            event_type=topic,
        )
        db.add(notification)
        db.commit()
        print(f"[Notification] ✉️  {subject} → user:{user_id}")

    except Exception as e:
        print(f"[Notification] Error handling event '{topic}': {e}")
    finally:
        db.close()


async def consume():
    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="notification-service",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    print("[Notification] Kafka consumer started, listening to topics:", TOPICS)
    try:
        async for msg in consumer:
            print(f"[Notification] Received: topic={msg.topic} key={msg.key}")
            await handle_event(msg.topic, msg.value)
    finally:
        await consumer.stop()
