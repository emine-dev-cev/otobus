import requests
import json
from datetime import datetime, timedelta, timezone
from jose import jwt

API_URL = "http://localhost:80"

def seed():
    # 1. Register/Login Admin (or just use a known secret if auth is mockable, 
    # but here we'll just try to get a token or use the service port directly to bypass gateway admin check if needed)
    # Actually, Trip Service /trips POST requires admin role in JWT.
    
    # We use the known secret key from docker-compose
    secret = "super-secret-key-change-in-production-123456"
    algo = "HS256"
    
    token = jwt.encode({
        "sub": "seed-admin",
        "role": "admin",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
    }, secret, algorithm=algo)
    
    headers = {"Authorization": f"Bearer {token}"}

    trips = [
        # Mevcut Seferler
        {
            "origin": "İstanbul",
            "destination": "Ankara",
            "departure_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=7)).isoformat(),
            "bus_name": "Metro Turizm",
            "bus_plate": "34 ABC 123",
            "total_seats": 40,
            "price": 450.0,
            "amenities": "Wi-Fi, Priz, TV, İkram",
            "description": "İstanbul-Ankara arası konforlu yolculuk. Bolu Dağı'nda 30 dakika mola verilmektedir. 2+1 geniş koltuklarla donatılmıştır.",
            "estimated_duration": "5s 0dk"
        },
        {
            "origin": "Ankara",
            "destination": "İzmir",
            "departure_time": (datetime.now() + timedelta(hours=5)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=13)).isoformat(),
            "bus_name": "Pamukkale Turizm",
            "bus_plate": "06 DEF 456",
            "total_seats": 38,
            "price": 600.0,
            "amenities": "Wi-Fi, 2+1 Koltuk, Tablet, Sıcak İkram",
            "description": "Ege'nin incisine konforlu ulaşım. Afyon'da Cumhuriyet Tesisleri'nde 40 dakika yöresel lezzet molası mevcuttur.",
            "estimated_duration": "8s 0dk"
        },
        {
            "origin": "İzmir",
            "destination": "Antalya",
            "departure_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(days=1, hours=7)).isoformat(),
            "bus_name": "Kamil Koç",
            "bus_plate": "35 GHI 789",
            "total_seats": 40,
            "price": 550.0,
            "amenities": "Priz, Geniş Koltuk, Su, USB Şarj",
            "description": "İzmir'den Akdeniz sahillerine panoramik manzaralı, kesintisiz rahat yolculuk.",
            "estimated_duration": "7s 0dk"
        },
        # Yeni Eklenen Seferler
        {
            "origin": "İstanbul",
            "destination": "Bursa",
            "departure_time": (datetime.now() + timedelta(hours=3)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=5, minutes=30)).isoformat(),
            "bus_name": "Nilüfer Turizm",
            "bus_plate": "16 NIL 16",
            "total_seats": 41,
            "price": 300.0,
            "amenities": "Wi-Fi, Priz, TV, 2+2 Koltuk, İkram",
            "description": "Osmangazi Köprüsü üzerinden beklemesiz ekspres Bursa seferi. Su ve soğuk içecek ikramı yapılmaktadır.",
            "estimated_duration": "2s 30dk"
        },
        {
            "origin": "İstanbul",
            "destination": "Trabzon",
            "departure_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(days=2, hours=4)).isoformat(),
            "bus_name": "Ali Osman Ulusoy",
            "bus_plate": "61 AOU 61",
            "total_seats": 38,
            "price": 1200.0,
            "amenities": "Wi-Fi, Priz, Tablet Ekran, Açık Büfe İkram, 2+1 VIP",
            "description": "Karadeniz sahil yolu manzarası eşliğinde konforlu Trabzon yolculuğu. Çorum ve Samsun'da özel tesis molaları.",
            "estimated_duration": "18s 0dk"
        },
        {
            "origin": "Ankara",
            "destination": "Gaziantep",
            "departure_time": (datetime.now() + timedelta(hours=8)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=18, minutes=30)).isoformat(),
            "bus_name": "Seç Turizm",
            "bus_plate": "27 SEC 27",
            "total_seats": 40,
            "price": 850.0,
            "amenities": "Wi-Fi, Priz, USB Şarj, Sıcak İkram, 2+1 Relax Koltuk",
            "description": "Gece seyahati ile sabah Gaziantep'e varış. Adana Pozantı tesislerinde dinlenme molası.",
            "estimated_duration": "10s 30dk"
        },
        {
            "origin": "Antalya",
            "destination": "İstanbul",
            "departure_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=14)).isoformat(),
            "bus_name": "Varan Turizm",
            "bus_plate": "07 VRN 34",
            "total_seats": 36,
            "price": 900.0,
            "amenities": "Yüksek Hızlı Wi-Fi, Priz, Multimedya, VIP Catering",
            "description": "Premium kalitede, geniş diz mesafesine sahip koltuklarla VIP Antalya-İstanbul seferi.",
            "estimated_duration": "13s 0dk"
        },
        {
            "origin": "Bursa",
            "destination": "Eskişehir",
            "departure_time": (datetime.now() + timedelta(hours=4)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=6, minutes=15)).isoformat(),
            "bus_name": "Efe Tur",
            "bus_plate": "26 EFE 41",
            "total_seats": 41,
            "price": 250.0,
            "amenities": "Wi-Fi, TV, Su",
            "description": "Kısa mesafe, direkt ve beklemesiz öğrenci dostu Eskişehir expres seferi.",
            "estimated_duration": "2s 15dk"
        },
        {
            "origin": "İzmir",
            "destination": "Adana",
            "departure_time": (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(days=2, hours=15)).isoformat(),
            "bus_name": "Has Turizm",
            "bus_plate": "01 HAS 01",
            "total_seats": 38,
            "price": 750.0,
            "amenities": "Priz, 2+1 Koltuk, Çay-Kahve İkramı, Okuma Lambası",
            "description": "Akdeniz'in iki büyük şehrini birbirine bağlayan güvenilir ring seferi. Tarsus ve Konya molalı.",
            "estimated_duration": "14s 0dk"
        },
        {
            "origin": "Trabzon",
            "destination": "Erzurum",
            "departure_time": (datetime.now() + timedelta(hours=12)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=16, minutes=45)).isoformat(),
            "bus_name": "Kamil Koç",
            "bus_plate": "25 KML 25",
            "total_seats": 40,
            "price": 400.0,
            "amenities": "Wi-Fi, Priz, Isıtmalı Koltuk, Kar Cebi, İkram",
            "description": "Doğu Anadolu'ya kısa ve güvenli bağlantı. Zigana Geçidi üzerinde fotoğraf molası opsiyonlu.",
            "estimated_duration": "4s 45dk"
        }
    ]


    for t in trips:
        res = requests.post(f"{API_URL}/trips", json=t, headers=headers)
        if res.status_code == 201:
            print(f"✅ Sefer oluşturuldu: {t['origin']} -> {t['destination']}")
        else:
            print(f"❌ Hata: {res.text}")

if __name__ == "__main__":
    # We might need to wait for services to be up if running via scripts
    seed()
