import sys
import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# Add service paths to sys.path to import models
sys.path.append(os.path.join(os.getcwd(), "services", "trip-service"))

from database import SessionLocal, engine, Base
from models import Company, Trip, Seat, TripStatus

def seed_data():
    db: Session = SessionLocal()
    
    print("Dropping and recreating tables in Trip Service...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 1. Create Companies
    companies_data = [
        {"name": "Metro Turizm", "logo_url": "https://upload.wikimedia.org/wikipedia/tr/0/03/Metro_Turizm_logo.png", "rating": 4.2, "contact": "0850 222 34 55"},
        {"name": "Pamukkale Turizm", "logo_url": "https://upload.wikimedia.org/wikipedia/tr/2/2c/Pamukkale_Turizm_Logo.png", "rating": 4.7, "contact": "0850 333 35 35"},
        {"name": "Kamil Koç", "logo_url": "https://upload.wikimedia.org/wikipedia/tr/a/a2/Kamil_Koc_logo.png", "rating": 4.5, "contact": "444 0 562"},
        {"name": "Varan Turizm", "logo_url": "https://seeklogo.com/images/V/varan-logo-0D9C1A6E7B-seeklogo.com.png", "rating": 4.8, "contact": "0850 222 8 222"},
    ]
    
    db_companies = []
    for c in companies_data:
        comp = Company(
            id=uuid.uuid4(),
            name=c["name"],
            logo_url=c["logo_url"],
            rating=c["rating"],
            contact_info=c["contact"]
        )
        db.add(comp)
        db_companies.append(comp)
    
    db.commit()

    # 2. Create Trips
    origins = ["İstanbul", "Ankara", "İzmir", "Antalya", "Bursa"]
    destinations = ["Ankara", "İstanbul", "Antalya", "İzmir", "Bursa"]
    bus_types = ["Mercedes Travego", "Neoplan Tourliner", "Setra S 517", "Temsa Maraton"]
    layouts = ["2+1", "2+2"]
    amenity_sets = [
        "WiFi, TV, İkram",
        "WiFi, USB, TV, Atıştırmalık",
        "WiFi, Geniş Koltuk, TV",
        "WiFi, İkram, 220V Priz"
    ]
    
    now = datetime.now(timezone.utc)
    
    print("Creating 20 trips with associated seats...")
    for i in range(20):
        if i < 4:
            origin = "İstanbul"
            dest = "Ankara"
        else:
            origin = random.choice(origins)
            dest = random.choice([d for d in destinations if d != origin])
        comp = random.choice(db_companies)
        layout = random.choice(layouts)
        
        # Randomize departure in next 30 days
        dep_time = now + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.choice([0, 15, 30, 45]))
        # Duration between 4 and 10 hours
        duration_hours = random.randint(4, 10)
        arr_time = dep_time + timedelta(hours=duration_hours)
        
        total_seats = 30 if layout == "2+1" else 40
        
        trip = Trip(
            id=uuid.uuid4(),
            origin=origin,
            destination=dest,
            departure_time=dep_time,
            arrival_time=arr_time,
            company_id=comp.id,
            bus_plate=f"{random.randint(10, 81)} AB {random.randint(100, 999)}",
            bus_type=random.choice(bus_types),
            bus_layout=layout,
            total_seats=total_seats,
            available_seats=total_seats,
            price=float(random.randrange(400, 1500, 50)),
            status=TripStatus.scheduled,
            amenities=random.choice(amenity_sets),
            description=f"{origin} - {dest} arası kesintisiz ve konforlu yolculuk deneyimi.",
            estimated_duration=f"{duration_hours} Saat"
        )
        db.add(trip)
        db.flush() 

        # 3. Create Seats for each trip
        for seat_num in range(1, total_seats + 1):
            seat = Seat(
                id=uuid.uuid4(),
                trip_id=trip.id,
                seat_number=seat_num,
                is_reserved=False
            )
            db.add(seat)
    
    db.commit()
    print("Success: Seed data successfully added.")
    db.close()

if __name__ == "__main__":
    seed_data()
