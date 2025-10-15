# README.md - placeholder
# 🤖 Nami Hospital Assistant Robot System


**Nami** is an advanced AI-powered hospital assistant robot system that combines voice interaction, intelligent task management, and autonomous navigation to streamline hospital operations.

## 🌟 Features

### 🎙️ Voice AI Agent
- **LiveKit + Google Gemini Realtime** integration
- Natural conversation with "Aoede" voice
- 17 specialized tools for hospital operations
- Real-time intent parsing and execution

### 🏥 Hospital Management
- **Doctor Management**: Schedules, specializations, availability
- **Patient Records**: Demographics, medical history, room assignments
- **Appointments**: Smart scheduling with conflict detection
- **Medicine Workflow**: Assignment, tracking, and delivery
- **Task Management**: Priority-based hospital tasks

### 🤖 Robot Operations
- **Navigation**: Autonomous movement through hospital
- **Medicine Delivery**: From pharmacy to patient rooms
- **Item Transport**: General delivery between locations
- **Status Monitoring**: Real-time robot telemetry

### 🚨 Emergency Response
- Code Blue and emergency alert system
- Staff notifications with priority levels
- Complete audit logging

## 📁 Project Structure

```
nami-hospital-assistant/
│
├── agent/                      # Voice AI Agent
│   ├── agent.py               # Main LiveKit agent
│   ├── prompts.py             # System prompts
│   ├── tools.py               # 17 tool functions
│   └── requirements.txt
│
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI server
│   ├── dummy_data.py          # Test data generator
│   ├── utils/
│   │   └── db.py              # MongoDB connection
│   ├── routes/                # API endpoints
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── medicines.py
│   │   ├── robot.py
│   │   ├── tasks.py
│   │   ├── queries.py
│   │   ├── confirm.py
│   │   ├── emergency.py
│   │   ├── notifications.py
│   │   └── logs.py
│   └── models/                # Pydantic models
│       ├── doctor.py
│       ├── patient.py
│       ├── appointment.py
│       ├── medicine.py
│       ├── task.py
│       ├── robot_command.py
│       ├── chatbot_log.py
│       ├── notification.py
│       └── emergency.py
│
├── client/                     # Robot Client
│   ├── rpi_client.py          # Simulated Raspberry Pi client
│   └── requirements.txt
│
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Backend container
├── .env.example                # Environment template
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB 7.0+
- LiveKit account (for voice agent)
- Google Gemini API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd nami-hospital-assistant

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Start MongoDB (Docker)

```bash
docker-compose up -d mongodb
```

Or install MongoDB locally.

### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the backend
python main.py
```

Backend will be available at `http://localhost:5000`

### 4. Load Test Data

```bash
# In another terminal (backend directory)
python dummy_data.py
```

This creates:
- 5 doctors
- 5 patients
- 4 appointments
- 4 medicine records
- 4 tasks
- Sample robot commands and notifications

### 5. Setup Voice Agent

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the agent
python agent.py dev
```

### 6. Start Robot Client

```bash
cd client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the robot simulator
python rpi_client.py
```

## 🎯 Usage Examples

### Voice Commands

**Appointment Booking:**
```
"Book appointment with Dr. Mehat at 11am for John"
→ Creates appointment, confirms with both parties
```

**Medicine Assignment:**
```
"Assign 2 Paracetamol tablets to John in Room 302"
→ Creates medicine record, schedules robot delivery
```

**Navigation:**
```
"Navigate to Room 405"
→ Robot moves to specified location
```

**Emergency:**
```
"Trigger Code Blue in Room 102"
→ Emergency alert sent to all staff, response team notified
```

**Information Queries:**
```
"What are visiting hours?"
→ Provides hospital policy information

"Who is the cardiologist on duty?"
→ Lists available cardiology doctors
```

### API Endpoints

Access the interactive API documentation at:
```
http://localhost:5000/docs
```

**Key Endpoints:**
- `GET /doctors` - List all doctors
- `POST /appointments` - Book appointment
- `POST /medicines/assign` - Assign medicine
- `GET /robot/commands/pending` - Get pending robot tasks
- `POST /emergency` - Trigger emergency alert
- `POST /queries` - Ask general questions

## 🛠️ Tool Functions (17 Total)

### Doctor Management
- `list_doctors()` - List doctors by specialization/availability
- `get_doctor_info()` - Get specific doctor details

### Patient Management
- `list_patients()` - List patients by room/status
- `get_patient_info()` - Get patient details and medical history

### Appointments
- `book_appointment()` - Schedule doctor appointments
- `list_appointments()` - View scheduled appointments

### Medicine Workflow
- `assign_medicine()` - Assign medication to patient
- `get_medicine_tasks()` - List pending deliveries
- `mark_medicine_delivered()` - Confirm delivery

### Robot Operations
- `navigate_to()` - Move robot to location
- `deliver_from_to()` - Transport items
- `get_robot_status()` - Check robot status
- `send_robot_command()` - Send custom commands

### Task Management
- `create_task()` - Create hospital task
- `list_tasks()` - View tasks by status/assignee
- `update_task_status()` - Update task progress

### Communication
- `notify_staff()` - Send notifications
- `trigger_emergency_alert()` - Emergency response
- `query()` - Answer general questions

## 🗄️ Database Schema

### Collections

**doctors**
```json
{
  "name": "Dr. Sarah Mehat",
  "specialization": "Cardiology",
  "room_number": "305",
  "available": true,
  "schedule": ["Mon", "Wed", "Fri"]
}
```

**patients**
```json
{
  "name": "John Doe",
  "age": 45,
  "room_number": "302",
  "status": "admitted",
  "allergies": ["Penicillin"],
  "assigned_doctor": "Dr. Sarah Mehat"
}
```

**appointments**
```json
{
  "doctor_name": "Dr. Mehat",
  "patient_name": "John",
  "date": "2025-10-12",
  "time": "11:00",
  "status": "scheduled"
}
```

**medicines**
```json
{
  "patient_name": "John Doe",
  "medicine_name": "Paracetamol",
  "dosage": "2 tablets",
  "room_number": "302",
  "status": "pending"
}
```

**robot_commands**
```json
{
  "intent": "medicine_delivery",
  "action": "deliver",
  "target": "Room 302",
  "status": "pending",
  "coordinates": {"x": 10.5, "y": 20.3}
}
```

## 🔧 Configuration

### Environment Variables

```bash
# LiveKit (required for voice agent)
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# Google Gemini (required)
GOOGLE_API_KEY=your_google_api_key

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=nami_hospital

# Backend
BACKEND_URL=http://localhost:5000
API_BASE=http://localhost:5000

# Robot
ROBOT_ID=NAMI-001
```

## 🐳 Docker Deployment

### Start All Services

```bash
docker-compose up -d
```

This starts:
- MongoDB on port 27017
- Backend API on port 5000

### View Logs

```bash
docker-compose logs -f backend
```

### Stop Services

```bash
docker-compose down
```

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:5000/health

# List doctors
curl http://localhost:5000/doctors

# Create appointment
curl -X POST http://localhost:5000/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_name": "Dr. Mehat",
    "patient_name": "John",
    "date": "2025-10-15",
    "time": "11:00",
    "reason": "Checkup"
  }'
```

### Test Robot Client

The robot client will automatically:
1. Poll for pending commands every 3 seconds
2. Execute commands sequentially
3. Log all activities to console
4. Update command status in database

## 📊 Monitoring

### View Logs

```bash
# Backend logs
cd backend
tail -f logs/nami.log

# Robot client logs
cd client
python rpi_client.py  # See live console output
```

### Database Queries

```bash
# Connect to MongoDB
mongosh nami_hospital

# View collections
show collections

# View recent logs
db.chatbot_logs.find().sort({timestamp: -1}).limit(10)

# View pending robot commands
db.robot_commands.find({status: "pending"})
```

## 🔒 Security Notes

- Never commit `.env` file with real credentials
- Use secure MongoDB authentication in production
- Implement proper authentication for API endpoints
- Use HTTPS for LiveKit in production
- Sanitize all user inputs
- Implement rate limiting on API endpoints

## 🛣️ Roadmap

- [ ] Web dashboard for monitoring
- [ ] Multi-robot coordination
- [ ] Advanced pathfinding algorithms
- [ ] Integration with hospital information systems
- [ ] Prescription management system

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check MongoDB connection
mongosh --eval "db.version()"

# Check port availability
lsof -i :5000
```

### Voice agent not responding
```bash
# Verify environment variables
echo $LIVEKIT_API_KEY
echo $GOOGLE_API_KEY

# Check LiveKit connection
# Visit LiveKit dashboard to verify room creation
```

### Robot client not receiving commands
```bash
# Check backend is running
curl http://localhost:5000/health

# Verify commands exist
curl http://localhost:5000/robot/commands/pending
```

## 📚 API Documentation

Full interactive API documentation available at:
```
http://localhost:5000/docs      # Swagger UI
http://localhost:5000/redoc     # ReDoc
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request



## 🙏 Acknowledgments

- **LiveKit** - Real-time communication platform
- **Google Gemini** - AI language model
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Email: Tusharhegde.dev@gmail.com


---

**Built with ❤️ for better healthcare as an project**

🏥 Nami Hospital Assistant - Making hospitals smarter, one task at a time.