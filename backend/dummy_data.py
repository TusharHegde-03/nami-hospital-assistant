"""
Generate Dummy Data for Testing
Run this script to populate the database with sample hospital data
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "nami_hospital")


async def generate_dummy_data():
    """Generate and insert dummy data"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    print("🔄 Generating dummy data...")
    
    # Clear existing data
    print("Clearing existing data...")
    await db.doctors.delete_many({})
    await db.patients.delete_many({})
    await db.appointments.delete_many({})
    await db.medicines.delete_many({})
    await db.tasks.delete_many({})
    await db.robot_commands.delete_many({})
    await db.notifications.delete_many({})
    await db.emergency_alerts.delete_many({})
    
    # Doctors
    doctors = [
        {
            "name": "Dr. Sarah Mehat",
            "specialization": "Cardiology",
            "room_number": "305",
            "phone": "+91-98765-43210",
            "email": "s.mehat@hospital.com",
            "available": True,
            "schedule": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Dr. Rajesh Kumar",
            "specialization": "Neurology",
            "room_number": "402",
            "phone": "+91-98765-43211",
            "email": "r.kumar@hospital.com",
            "available": True,
            "schedule": ["Mon", "Wed", "Fri"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Dr. Priya Sharma",
            "specialization": "Pediatrics",
            "room_number": "201",
            "phone": "+91-98765-43212",
            "email": "p.sharma@hospital.com",
            "available": True,
            "schedule": ["Tue", "Thu", "Sat"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Dr. Amit Patel",
            "specialization": "Orthopedics",
            "room_number": "308",
            "phone": "+91-98765-43213",
            "email": "a.patel@hospital.com",
            "available": True,
            "schedule": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Dr. Neha Gupta",
            "specialization": "General Medicine",
            "room_number": "105",
            "phone": "+91-98765-43214",
            "email": "n.gupta@hospital.com",
            "available": False,
            "schedule": ["Mon", "Wed", "Fri"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.doctors.insert_many(doctors)
    print(f"✅ Inserted {len(result.inserted_ids)} doctors")
    
    # Patients
    patients = [
        {
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "room_number": "302",
            "blood_type": "O+",
            "status": "admitted",
            "admission_date": datetime.utcnow() - timedelta(days=3),
            "phone": "+91-98765-12345",
            "emergency_contact": "+91-98765-12346",
            "allergies": ["Penicillin"],
            "medical_conditions": ["Diabetes", "Hypertension"],
            "assigned_doctor": "Dr. Sarah Mehat",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Jane Smith",
            "age": 32,
            "gender": "Female",
            "room_number": "405",
            "blood_type": "A+",
            "status": "admitted",
            "admission_date": datetime.utcnow() - timedelta(days=1),
            "phone": "+91-98765-22345",
            "emergency_contact": "+91-98765-22346",
            "allergies": [],
            "medical_conditions": ["Asthma"],
            "assigned_doctor": "Dr. Rajesh Kumar",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Rahul Verma",
            "age": 28,
            "gender": "Male",
            "room_number": "201",
            "blood_type": "B+",
            "status": "critical",
            "admission_date": datetime.utcnow(),
            "phone": "+91-98765-32345",
            "emergency_contact": "+91-98765-32346",
            "allergies": ["Sulfa drugs"],
            "medical_conditions": ["Cardiac arrest"],
            "assigned_doctor": "Dr. Sarah Mehat",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Anita Singh",
            "age": 55,
            "gender": "Female",
            "room_number": "308",
            "blood_type": "AB+",
            "status": "admitted",
            "admission_date": datetime.utcnow() - timedelta(days=5),
            "phone": "+91-98765-42345",
            "emergency_contact": "+91-98765-42346",
            "allergies": [],
            "medical_conditions": ["Osteoporosis"],
            "assigned_doctor": "Dr. Amit Patel",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Michael Johnson",
            "age": 67,
            "gender": "Male",
            "room_number": "102",
            "blood_type": "O-",
            "status": "admitted",
            "admission_date": datetime.utcnow() - timedelta(days=7),
            "phone": "+91-98765-52345",
            "emergency_contact": "+91-98765-52346",
            "allergies": ["Latex"],
            "medical_conditions": ["COPD", "Heart disease"],
            "assigned_doctor": "Dr. Neha Gupta",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.patients.insert_many(patients)
    print(f"✅ Inserted {len(result.inserted_ids)} patients")
    
    # Appointments
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    appointments = [
        {
            "doctor_name": "Dr. Sarah Mehat",
            "patient_name": "John Doe",
            "date": today.isoformat(),
            "time": "11:00",
            "reason": "Cardiac checkup",
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "doctor_name": "Dr. Rajesh Kumar",
            "patient_name": "Jane Smith",
            "date": today.isoformat(),
            "time": "14:00",
            "reason": "Neurological assessment",
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "doctor_name": "Dr. Amit Patel",
            "patient_name": "Anita Singh",
            "date": tomorrow.isoformat(),
            "time": "10:00",
            "reason": "Bone density test review",
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "doctor_name": "Dr. Priya Sharma",
            "patient_name": "Michael Johnson",
            "date": tomorrow.isoformat(),
            "time": "15:30",
            "reason": "General consultation",
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.appointments.insert_many(appointments)
    print(f"✅ Inserted {len(result.inserted_ids)} appointments")
    
    # Medicines
    medicines = [
        {
            "patient_name": "John Doe",
            "medicine_name": "Metformin",
            "dosage": "500mg",
            "frequency": "Twice daily",
            "room_number": "302",
            "status": "pending",
            "assigned_at": datetime.utcnow(),
            "delivered_at": None,
            "notes": "Take with meals"
        },
        {
            "patient_name": "John Doe",
            "medicine_name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "Once daily",
            "room_number": "302",
            "status": "delivered",
            "assigned_at": datetime.utcnow() - timedelta(hours=2),
            "delivered_at": datetime.utcnow() - timedelta(hours=1),
            "notes": "Morning dose"
        },
        {
            "patient_name": "Jane Smith",
            "medicine_name": "Albuterol",
            "dosage": "2 puffs",
            "frequency": "As needed",
            "room_number": "405",
            "status": "pending",
            "assigned_at": datetime.utcnow(),
            "delivered_at": None,
            "notes": "For emergency use"
        },
        {
            "patient_name": "Rahul Verma",
            "medicine_name": "Aspirin",
            "dosage": "325mg",
            "frequency": "Once daily",
            "room_number": "201",
            "status": "assigned",
            "assigned_at": datetime.utcnow(),
            "delivered_at": None,
            "notes": "Blood thinner - URGENT"
        }
    ]
    
    result = await db.medicines.insert_many(medicines)
    print(f"✅ Inserted {len(result.inserted_ids)} medicine records")
    
    # Tasks
    tasks = [
        {
            "title": "Clean Room 302",
            "description": "Daily cleaning and sanitization",
            "assigned_to": "Housekeeping",
            "priority": "medium",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "due_date": None
        },
        {
            "title": "Equipment maintenance - ICU",
            "description": "Check all ventilators and monitors",
            "assigned_to": "Technical Team",
            "priority": "high",
            "status": "in_progress",
            "created_at": datetime.utcnow() - timedelta(hours=1),
            "updated_at": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(hours=2)
        },
        {
            "title": "Inventory check - Pharmacy",
            "description": "Weekly medicine inventory audit",
            "assigned_to": "Pharmacy Staff",
            "priority": "medium",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=1)
        },
        {
            "title": "Patient transfer to ICU",
            "description": "Transfer Rahul Verma from Room 201 to ICU",
            "assigned_to": "Nursing Staff",
            "priority": "urgent",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(minutes=30)
        }
    ]
    
    result = await db.tasks.insert_many(tasks)
    print(f"✅ Inserted {len(result.inserted_ids)} tasks")
    
    # Robot Commands
    robot_commands = [
        {
            "intent": "navigation",
            "action": "navigate",
            "target": "Room 302",
            "coordinates": {"x": 10.5, "y": 20.3},
            "details": None,
            "status": "completed",
            "timestamp": datetime.utcnow() - timedelta(minutes=30),
            "completed_at": datetime.utcnow() - timedelta(minutes=25),
            "error_message": None
        },
        {
            "intent": "medicine_delivery",
            "action": "deliver",
            "target": "Room 405",
            "coordinates": {"x": 15.2, "y": 35.7},
            "details": {
                "medicine": "Albuterol",
                "patient": "Jane Smith",
                "dosage": "2 puffs"
            },
            "status": "pending",
            "timestamp": datetime.utcnow(),
            "completed_at": None,
            "error_message": None
        }
    ]
    
    result = await db.robot_commands.insert_many(robot_commands)
    print(f"✅ Inserted {len(result.inserted_ids)} robot commands")
    
    # Notifications
    notifications = [
        {
            "recipient": "Dr. Sarah Mehat",
            "message": "Patient John Doe's test results are ready",
            "priority": "normal",
            "status": "sent",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "read_at": None
        },
        {
            "recipient": "Nursing Staff",
            "message": "Medicine delivery required for Room 405",
            "priority": "high",
            "status": "sent",
            "timestamp": datetime.utcnow(),
            "read_at": None
        },
        {
            "recipient": "Emergency Team",
            "message": "Patient in Room 201 requires immediate attention",
            "priority": "urgent",
            "status": "read",
            "timestamp": datetime.utcnow() - timedelta(minutes=15),
            "read_at": datetime.utcnow() - timedelta(minutes=10)
        }
    ]
    
    result = await db.notifications.insert_many(notifications)
    print(f"✅ Inserted {len(result.inserted_ids)} notifications")
    
    print("\n✅ All dummy data generated successfully!")
    print("\n📊 Summary:")
    print(f"  - Doctors: {len(doctors)}")
    print(f"  - Patients: {len(patients)}")
    print(f"  - Appointments: {len(appointments)}")
    print(f"  - Medicines: {len(medicines)}")
    print(f"  - Tasks: {len(tasks)}")
    print(f"  - Robot Commands: {len(robot_commands)}")
    print(f"  - Notifications: {len(notifications)}")
    
    client.close()


if __name__ == "__main__":
    print("🏥 Nami Hospital Assistant - Dummy Data Generator")
    print("=" * 60)
    asyncio.run(generate_dummy_data())