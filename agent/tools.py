# tools.py - corrected with @function_tool decorator
"""
Nami Hospital Assistant - Tool Functions
All tools call backend API endpoints using httpx
"""

import httpx
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from livekit.agents.llm import function_tool  # Add this import

API_BASE = os.getenv("API_BASE", "http://localhost:5000")

async def log_interaction(query: str, intent: str, action: str, target: str, response: str):
    """Log all chatbot interactions to MongoDB"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{API_BASE}/logs", json={
                "query": query,
                "intent": intent,
                "action": action,
                "target": target,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Logging failed: {e}")

# ==================== DOCTOR TOOLS ====================

@function_tool()
async def list_doctors(specialization: Optional[str] = None, available: bool = False) -> str:
    """
    List all doctors, optionally filtered by specialization or availability.
    
    Args:
        specialization: Filter by medical specialization (cardiology, neurology, etc.)
        available: Only show currently available doctors
    
    Returns:
        Formatted list of doctors with their details
    """
    async with httpx.AsyncClient() as client:
        params = {}
        if specialization:
            params["specialization"] = specialization
        if available:
            params["available"] = "true"
        
        response = await client.get(f"{API_BASE}/doctors", params=params)
        doctors = response.json()
        
        if not doctors:
            return "No doctors found matching your criteria."
        
        result = f"Found {len(doctors)} doctor(s):\n"
        for doc in doctors[:5]:  # Limit to 5 for voice readability
            result += f"- Dr. {doc['name']}, {doc['specialization']}, Room {doc['room_number']}\n"
        
        await log_interaction(
            query=f"list_doctors(specialization={specialization}, available={available})",
            intent="doctor",
            action="list",
            target=specialization or "all",
            response=result
        )
        
        return result

# ==================== PATIENT TOOLS ====================

@function_tool()
async def list_patients(room_number: Optional[str] = None, status: Optional[str] = None) -> str:
    """
    List patients, optionally filtered by room or status.
    
    Args:
        room_number: Filter by room number
        status: Filter by patient status (admitted, discharged, critical)
    
    Returns:
        Formatted list of patients
    """
    async with httpx.AsyncClient() as client:
        params = {}
        if room_number:
            params["room_number"] = room_number
        if status:
            params["status"] = status
        
        response = await client.get(f"{API_BASE}/patients", params=params)
        patients = response.json()
        
        if not patients:
            return "No patients found matching your criteria."
        
        result = f"Found {len(patients)} patient(s):\n"
        for patient in patients[:5]:
            result += f"- {patient['name']}, Room {patient['room_number']}, Status: {patient['status']}\n"
        
        await log_interaction(
            query=f"list_patients(room={room_number}, status={status})",
            intent="patient",
            action="list",
            target=room_number or status or "all",
            response=result
        )
        
        return result

@function_tool()
async def get_patient_info(patient_id: Optional[str] = None, name: Optional[str] = None) -> str:
    """
    Get detailed information about a specific patient.
    
    Args:
        patient_id: Patient ID number
        name: Patient name
    
    Returns:
        Detailed patient information
    """
    async with httpx.AsyncClient() as client:
        if patient_id:
            response = await client.get(f"{API_BASE}/patients/{patient_id}")
        elif name:
            response = await client.get(f"{API_BASE}/patients", params={"name": name})
            patients = response.json()
            if not patients:
                return f"No patient found with name {name}"
            patient = patients[0]
            return f"Patient: {patient['name']}, Room: {patient['room_number']}, Status: {patient['status']}, Age: {patient['age']}"
        else:
            return "Please provide either patient ID or name"
        
        patient = response.json()
        result = f"Patient: {patient['name']}, Room: {patient['room_number']}, Status: {patient['status']}, Age: {patient['age']}, Blood Type: {patient.get('blood_type', 'N/A')}"
        
        await log_interaction(
            query=f"get_patient_info({patient_id or name})",
            intent="patient",
            action="get_info",
            target=patient_id or name,
            response=result
        )
        
        return result

# ==================== APPOINTMENT TOOLS ====================

@function_tool()
async def book_appointment(doctor_name: str, patient_name: str, date: str, time: str, reason: Optional[str] = None) -> str:
    """
    Book a medical appointment.
    
    Args:
        doctor_name: Name of the doctor
        patient_name: Name of the patient
        date: Appointment date (YYYY-MM-DD or 'today', 'tomorrow')
        time: Appointment time (HH:MM or '11am')
        reason: Reason for appointment (optional)
    
    Returns:
        Confirmation message
    """
    async with httpx.AsyncClient() as client:
        # Parse date and time
        if date.lower() == "today":
            date = datetime.now().strftime("%Y-%m-%d")
        elif date.lower() == "tomorrow":
            from datetime import timedelta
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Convert time format
        if "am" in time.lower() or "pm" in time.lower():
            time = datetime.strptime(time, "%I%p").strftime("%H:%M")
        
        payload = {
            "doctor_name": doctor_name,
            "patient_name": patient_name,
            "date": date,
            "time": time,
            "reason": reason or "General consultation",
            "status": "scheduled"
        }
        
        response = await client.post(f"{API_BASE}/appointments", json=payload)
        appointment = response.json()
        
        result = f"Appointment booked: Dr. {doctor_name} with {patient_name} on {date} at {time}. Confirmation ID: {appointment.get('_id', 'N/A')}"
        
        await log_interaction(
            query=f"book_appointment({doctor_name}, {patient_name}, {date}, {time})",
            intent="appointment",
            action="book",
            target=doctor_name,
            response=result
        )
        
        return result

# ==================== MEDICINE TOOLS ====================

@function_tool()
async def assign_medicine(patient_name: str, medicine_name: str, dosage: str, frequency: str, room_number: Optional[str] = None) -> str:
    """
    Assign medicine to a patient.
    
    Args:
        patient_name: Name of the patient
        medicine_name: Name of the medication
        dosage: Dosage amount (e.g., "2 tablets", "10ml")
        frequency: How often (e.g., "twice daily", "every 6 hours")
        room_number: Patient's room number (optional)
    
    Returns:
        Confirmation with delivery status
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "patient_name": patient_name,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "frequency": frequency,
            "room_number": room_number,
            "status": "pending",
            "assigned_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/medicines/assign", json=payload)
        medicine_record = response.json()
        
        # Also create a robot delivery command
        robot_payload = {
            "intent": "medicine_delivery",
            "action": "deliver",
            "target": room_number or "patient room",
            "details": {
                "medicine": medicine_name,
                "patient": patient_name,
                "dosage": dosage
            },
            "status": "pending"
        }
        await client.post(f"{API_BASE}/robot/commands", json=robot_payload)
        
        result = f"Assigned {dosage} of {medicine_name} to {patient_name}. Delivery scheduled to room {room_number or 'TBD'}."
        
        await log_interaction(
            query=f"assign_medicine({patient_name}, {medicine_name}, {dosage})",
            intent="medicine",
            action="assign",
            target=patient_name,
            response=result
        )
        
        return result

@function_tool()
async def get_medicine_tasks(status: Optional[str] = None) -> str:
    """
    Get pending medicine delivery tasks.
    
    Args:
        status: Filter by status (pending, in_progress, delivered)
    
    Returns:
        List of medicine tasks
    """
    async with httpx.AsyncClient() as client:
        params = {"type": "medicine"}
        if status:
            params["status"] = status
        
        response = await client.get(f"{API_BASE}/medicines", params=params)
        medicines = response.json()
        
        if not medicines:
            return "No medicine tasks found."
        
        result = f"Found {len(medicines)} medicine task(s):\n"
        for med in medicines[:5]:
            result += f"- {med['medicine_name']} for {med['patient_name']}, Room {med.get('room_number', 'N/A')}, Status: {med['status']}\n"
        
        return result

@function_tool()
async def mark_medicine_delivered(medicine_id: str) -> str:
    """
    Mark a medicine as delivered.
    
    Args:
        medicine_id: ID of the medicine record
    
    Returns:
        Confirmation message
    """
    async with httpx.AsyncClient() as client:
        payload = {"status": "delivered", "delivered_at": datetime.utcnow().isoformat()}
        response = await client.patch(f"{API_BASE}/medicines/{medicine_id}", json=payload)
        
        result = "Medicine delivery confirmed."
        
        await log_interaction(
            query=f"mark_medicine_delivered({medicine_id})",
            intent="medicine",
            action="delivered",
            target=medicine_id,
            response=result
        )
        
        return result

# ==================== ROBOT NAVIGATION TOOLS ====================

@function_tool()
async def navigate_to(location: str, coordinates: Optional[Dict[str, float]] = None) -> str:
    """
    Navigate robot to a specific location.
    
    Args:
        location: Room number or location name (e.g., "Room 405", "ICU", "Pharmacy")
        coordinates: Optional x, y coordinates
    
    Returns:
        Navigation status
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "intent": "navigation",
            "action": "navigate",
            "target": location,
            "coordinates": coordinates,
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/robot/commands", json=payload)
        command = response.json()
        
        result = f"Navigating to {location}. Estimated arrival: 2 minutes."
        
        await log_interaction(
            query=f"navigate_to({location})",
            intent="navigation",
            action="navigate",
            target=location,
            response=result
        )
        
        return result

@function_tool()
async def deliver_from_to(item: str, from_location: str, to_location: str) -> str:
    """
    Deliver an item from one location to another.
    
    Args:
        item: Item to deliver
        from_location: Pickup location
        to_location: Delivery location
    
    Returns:
        Delivery status
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "intent": "delivery",
            "action": "deliver",
            "target": to_location,
            "details": {
                "item": item,
                "from": from_location,
                "to": to_location
            },
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/robot/commands", json=payload)
        
        result = f"Delivering {item} from {from_location} to {to_location}. Starting now."
        
        await log_interaction(
            query=f"deliver_from_to({item}, {from_location}, {to_location})",
            intent="delivery",
            action="deliver",
            target=to_location,
            response=result
        )
        
        return result

@function_tool()
async def get_robot_status() -> str:
    """
    Get current robot status and location.
    
    Returns:
        Robot status information
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/robot/status")
        status = response.json()
        
        result = f"Robot Status: {status.get('status', 'idle')}, Location: {status.get('location', 'unknown')}, Battery: {status.get('battery', 100)}%"
        
        return result

@function_tool()
async def send_robot_command(command: str, target: Optional[str] = None) -> str:
    """
    Send a custom command to the robot.
    
    Args:
        command: Command to execute (stop, resume, return_home, etc.)
        target: Optional target parameter
    
    Returns:
        Command execution status
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "intent": "robot_control",
            "action": command,
            "target": target or "robot",
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/robot/commands", json=payload)
        
        result = f"Robot command '{command}' sent successfully."
        
        await log_interaction(
            query=f"send_robot_command({command})",
            intent="robot_control",
            action=command,
            target=target or "robot",
            response=result
        )
        
        return result

# ==================== TASK MANAGEMENT TOOLS ====================

@function_tool()
async def create_task(title: str, description: str, assigned_to: Optional[str] = None, priority: str = "medium") -> str:
    """
    Create a new hospital task.
    
    Args:
        title: Task title
        description: Task description
        assigned_to: Staff member to assign task to
        priority: Task priority (low, medium, high, urgent)
    
    Returns:
        Task creation confirmation
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/tasks", json=payload)
        task = response.json()
        
        result = f"Task created: '{title}' assigned to {assigned_to or 'unassigned'} with {priority} priority."
        
        await log_interaction(
            query=f"create_task({title})",
            intent="task",
            action="create",
            target=title,
            response=result
        )
        
        return result

@function_tool()
async def list_tasks(status: Optional[str] = None, assigned_to: Optional[str] = None) -> str:
    """
    List hospital tasks.
    
    Args:
        status: Filter by status (pending, in_progress, completed)
        assigned_to: Filter by assigned staff member
    
    Returns:
        List of tasks
    """
    async with httpx.AsyncClient() as client:
        params = {}
        if status:
            params["status"] = status
        if assigned_to:
            params["assigned_to"] = assigned_to
        
        response = await client.get(f"{API_BASE}/tasks", params=params)
        tasks = response.json()
        
        if not tasks:
            return "No tasks found."
        
        result = f"Found {len(tasks)} task(s):\n"
        for task in tasks[:5]:
            result += f"- {task['title']}: {task['status']}, Priority: {task['priority']}\n"
        
        return result

@function_tool()
async def update_task_status(task_id: str, status: str) -> str:
    """
    Update task status.
    
    Args:
        task_id: Task ID
        status: New status (pending, in_progress, completed, cancelled)
    
    Returns:
        Update confirmation
    """
    async with httpx.AsyncClient() as client:
        payload = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        response = await client.patch(f"{API_BASE}/tasks/{task_id}", json=payload)
        
        result = f"Task status updated to {status}."
        
        await log_interaction(
            query=f"update_task_status({task_id}, {status})",
            intent="task",
            action="update",
            target=task_id,
            response=result
        )
        
        return result

# ==================== NOTIFICATION TOOLS ====================

@function_tool()
async def notify_staff(recipient: str, message: str, priority: str = "normal") -> str:
    """
    Send notification to hospital staff.
    
    Args:
        recipient: Staff member name or department
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
    
    Returns:
        Notification confirmation
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "recipient": recipient,
            "message": message,
            "priority": priority,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/notifications", json=payload)
        
        result = f"Notification sent to {recipient}: {message}"
        
        await log_interaction(
            query=f"notify_staff({recipient}, {message})",
            intent="notification",
            action="send",
            target=recipient,
            response=result
        )
        
        return result

# ==================== EMERGENCY TOOLS ====================

@function_tool()
async def trigger_emergency_alert(alert_type: str, location: str, details: Optional[str] = None) -> str:
    """
    Trigger hospital emergency alert.
    
    Args:
        alert_type: Type of emergency (code_blue, code_red, fire, etc.)
        location: Location of emergency
        details: Additional details
    
    Returns:
        Emergency alert confirmation
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "alert_type": alert_type,
            "location": location,
            "details": details,
            "status": "active",
            "triggered_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(f"{API_BASE}/emergency", json=payload)
        alert = response.json()
        
        result = f"EMERGENCY ALERT: {alert_type.upper()} triggered at {location}. All emergency personnel notified."
        
        await log_interaction(
            query=f"trigger_emergency_alert({alert_type}, {location})",
            intent="emergency",
            action="trigger",
            target=location,
            response=result
        )
        
        return result

# ==================== QUERY TOOLS ====================

@function_tool()
async def query(question: str) -> str:
    """
    Answer general questions using Gemini AI.
    
    Args:
        question: The question to answer
    
    Returns:
        Answer to the question
    """
    async with httpx.AsyncClient() as client:
        payload = {"query": question}
        response = await client.post(f"{API_BASE}/queries", json=payload, timeout=30.0)
        result_data = response.json()
        
        answer = result_data.get("answer", "I'm not sure about that.")
        
        await log_interaction(
            query=question,
            intent="query",
            action="answer",
            target="general",
            response=answer
        )
        
        return answer


# Tool registry for LiveKit agent - Now these are decorated functions
TOOL_REGISTRY = {
    "list_doctors": list_doctors,
    "list_patients": list_patients,
    "get_patient_info": get_patient_info,
    "book_appointment": book_appointment,
    "assign_medicine": assign_medicine,
    "get_medicine_tasks": get_medicine_tasks,
    "mark_medicine_delivered": mark_medicine_delivered,
    "navigate_to": navigate_to,
    "deliver_from_to": deliver_from_to,
    "get_robot_status": get_robot_status,
    "send_robot_command": send_robot_command,
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task_status": update_task_status,
    "notify_staff": notify_staff,
    "trigger_emergency_alert": trigger_emergency_alert,
    "query": query
}