"""
Raspberry Pi Robot Client
Simulates a robot that polls for commands and executes them
"""

import asyncio
import httpx
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:5000")
ROBOT_ID = os.getenv("ROBOT_ID", "NAMI-001")
POLL_INTERVAL = 3  # seconds


class RobotClient:
    """Simulated hospital robot client"""
    
    def __init__(self):
        self.robot_id = ROBOT_ID
        self.current_location = "Lobby"
        self.battery = 100
        self.status = "idle"
        self.current_task = None
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 {self.robot_id}: {message}")
    
    async def update_status(self):
        """Report status to backend"""
        async with httpx.AsyncClient() as client:
            try:
                # In a real robot, this would send actual telemetry
                pass
            except Exception as e:
                self.log(f"Status update failed: {e}")
    
    async def navigate_to(self, target: str, coordinates: dict = None):
        """Simulate navigation to a location"""
        self.log(f"🚀 Starting navigation to {target}")
        self.status = "navigating"
        
        # Simulate movement time (2-5 seconds)
        travel_time = 3
        for i in range(travel_time):
            await asyncio.sleep(1)
            self.log(f"  Moving... ({i+1}/{travel_time}s)")
        
        self.current_location = target
        self.status = "idle"
        self.log(f"✅ Arrived at {target}")
    
    async def deliver_item(self, item: str, details: dict):
        """Simulate item delivery"""
        self.log(f"📦 Delivering: {item}")
        
        # Navigate to pickup location if specified
        if details.get("from"):
            await self.navigate_to(details["from"])
            self.log(f"  Picked up {item}")
            await asyncio.sleep(1)
        
        # Navigate to delivery location
        if details.get("to"):
            await self.navigate_to(details["to"])
            self.log(f"  Delivered {item}")
    
    async def deliver_medicine(self, details: dict):
        """Simulate medicine delivery"""
        medicine = details.get("medicine", "medicine")
        patient = details.get("patient", "patient")
        dosage = details.get("dosage", "")
        
        self.log(f"💊 Medicine Delivery: {dosage} {medicine} for {patient}")
        
        # Go to pharmacy
        await self.navigate_to("Pharmacy")
        self.log(f"  Collected {medicine} from pharmacy")
        await asyncio.sleep(1)
        
        # Deliver to patient room
        room = details.get("room", "unknown room")
        await self.navigate_to(room)
        self.log(f"  ✅ Delivered {medicine} to {patient}")
    
    async def execute_command(self, command: dict):
        """Execute a robot command"""
        command_id = str(command["_id"])
        intent = command["intent"]
        action = command["action"]
        target = command["target"]
        details = command.get("details", {})
        
        self.log(f"📋 Executing: {intent} - {action} -> {target}")
        self.current_task = command_id
        
        # Mark as executing
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{API_BASE}/robot/commands/{command_id}/execute")
            except:
                pass
        
        try:
            # Execute based on intent
            if intent == "navigation":
                await self.navigate_to(target, command.get("coordinates"))
            
            elif intent == "delivery":
                item = details.get("item", "item")
                await self.deliver_item(item, details)
            
            elif intent == "medicine_delivery":
                await self.deliver_medicine(details)
            
            elif intent == "robot_control":
                if action == "stop":
                    self.log("⏸️  Robot stopped")
                    self.status = "stopped"
                elif action == "resume":
                    self.log("▶️  Robot resumed")
                    self.status = "idle"
                elif action == "return_home":
                    await self.navigate_to("Lobby")
                else:
                    self.log(f"Unknown robot control action: {action}")
            
            else:
                self.log(f"⚠️  Unknown intent: {intent}")
            
            # Mark as completed
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        f"{API_BASE}/robot/commands/{command_id}/complete",
                        params={"success": True}
                    )
                    self.log(f"✅ Command completed successfully")
                except Exception as e:
                    self.log(f"Failed to mark command as complete: {e}")
        
        except Exception as e:
            self.log(f"❌ Command execution failed: {e}")
            
            # Mark as failed
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        f"{API_BASE}/robot/commands/{command_id}/complete",
                        params={"success": False, "error_message": str(e)}
                    )
                except:
                    pass
        
        finally:
            self.current_task = None
            self.status = "idle"
    
    async def poll_for_commands(self):
        """Poll backend for new commands"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_BASE}/robot/commands/pending")
                commands = response.json()
                
                if commands:
                    # Execute the oldest pending command
                    command = commands[0]
                    await self.execute_command(command)
                    
            except httpx.ConnectError:
                self.log("❌ Cannot connect to backend server")
            except Exception as e:
                self.log(f"Error polling for commands: {e}")
    
    async def run(self):
        """Main robot loop"""
        self.log(f"🚀 Starting robot client")
        self.log(f"📍 Initial location: {self.current_location}")
        self.log(f"🔋 Battery: {self.battery}%")
        self.log(f"🔗 Connected to: {API_BASE}")
        self.log(f"⏱️  Polling interval: {POLL_INTERVAL}s")
        print("")
        
        while True:
            try:
                if self.status == "idle":
                    await self.poll_for_commands()
                
                # Simulate battery drain
                if self.battery > 0:
                    self.battery -= 0.1
                
                # Report status periodically
                await self.update_status()
                
                # Wait before next poll
                await asyncio.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                self.log("👋 Shutting down robot client")
                break
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                await asyncio.sleep(POLL_INTERVAL)


async def main():
    """Entry point"""
    print("=" * 70)
    print("🤖 NAMI HOSPITAL ASSISTANT ROBOT CLIENT")
    print("=" * 70)
    print("")
    
    robot = RobotClient()
    await robot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Robot client stopped by user")