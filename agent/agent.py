"""
Nami Hospital Assistant - Main Voice Agent
LiveKit + Google Gemini Realtime Integration
Updated to Recent LiveKit API
"""

import asyncio
import logging
import os
import re
from datetime import datetime
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents import RoomInputOptions
from livekit.plugins import google, noise_cancellation

from prompts import SYSTEM_PROMPT
from tools import TOOL_REGISTRY


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hospital configuration
HOSPITAL_NAME = os.getenv("HOSPITAL_NAME", "City General Hospital")
ROBOT_ID = os.getenv("ROBOT_ID", "NAMI-001")

# Wake words and stop words
WAKE_WORDS = ["hey nami", "hello nami", "wake up", "start assistant", "nami"]
STOP_WORDS = ["stop", "exit", "goodbye", "thank you", "that's all", "end session"]


class NamiAssistant(Agent):
    """Nami Hospital Assistant Voice Agent"""
    
    def __init__(self):
        self.robot_location = "Lobby"
        self.robot_status = "Ready"
        self.hospital_name = HOSPITAL_NAME
        self.is_active = False
        
        # Generate dynamic system prompt with current context
        dynamic_instruction = self._get_system_prompt()
        
        # Initialize tools from your registry
        tool_list = list(TOOL_REGISTRY.values())
        
        super().__init__(
            instructions=dynamic_instruction,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",  # Natural female voice
                temperature=0.7,
            ),
            tools=tool_list,
        )
    
    def _get_system_prompt(self) -> str:
        """Generate dynamic system prompt with current context"""
        return SYSTEM_PROMPT.format(
            hospital_name=HOSPITAL_NAME,
            current_date=datetime.now().strftime("%A, %B %d, %Y"),
            robot_location=self.robot_location,
            robot_status=self.robot_status,
            robot_id=ROBOT_ID
        )


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the voice agent"""
    
    logger.info(f"Starting Nami Hospital Assistant ({ROBOT_ID})...")
    logger.info(f"Hospital: {HOSPITAL_NAME}")
    logger.info(f"Room: {ctx.room.name}")
    
    # Connect to room first
    await ctx.connect()
    logger.info("Connected to LiveKit room")
    
    # Create agent session
    session = AgentSession()
    nami_agent = NamiAssistant()
    
    # State management
    is_awake = False
    conversation_active = False
    
    def check_wake_word(text: str) -> bool:
        """Check if user said a wake word"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in WAKE_WORDS)
    
    def check_stop_word(text: str) -> bool:
        """Check if user said a stop word"""
        text_lower = text.lower()
        return any(stop_word in text_lower for stop_word in STOP_WORDS)
    
    # Add event listeners for conversation logging
    @session.on("user_speech_committed")
    def on_user_speech(event):
        """Log user speech to console and handle wake/stop words"""
        nonlocal is_awake, conversation_active
        user_text = event.message
        
        print(f"\n🧑 USER: {user_text}")
        logger.info(f"User said: {user_text}")
        
        # Check for wake word if not awake
        if not is_awake and check_wake_word(user_text):
            print("\n🔔 WAKE WORD DETECTED! Activating Nami...")
            logger.info("Wake word detected, activating agent")
            is_awake = True
            conversation_active = True
            
            # Start the session if not already started
            asyncio.create_task(start_session())
            
        # Check for stop word if awake
        elif is_awake and check_stop_word(user_text):
            print("\n🛑 STOP WORD DETECTED! Deactivating Nami...")
            logger.info("Stop word detected, deactivating agent")
            is_awake = False
            conversation_active = False
            
            # Say goodbye
            asyncio.create_task(session.generate_reply(
                instructions="The user has ended the conversation. Say a polite goodbye and let them know you're going back to sleep mode.",
            ))
    
    @session.on("agent_speech_committed")
    def on_agent_speech(event):
        """Log agent speech to console"""
        agent_text = event.message
        print(f"\n🤖 NAMI: {agent_text}")
        logger.info(f"Agent said: {agent_text}")
    
    @session.on("function_calls_finished")
    def on_function_calls(event):
        """Log function calls to console"""
        for call in event.calls:
            print(f"\n🔧 TOOL EXECUTED: {call.function_name}")
            print(f"   Input: {call.function_args}")
            print(f"   Result: {call.result}")
            logger.info(f"Tool executed - {call.function_name}: {call.result}")
    
    @session.on("agent_started_speaking")
    def on_agent_start_speaking():
        """Log when agent starts speaking"""
        print("\n🎤 Nami is speaking...")
        logger.info("Agent started speaking")
    
    @session.on("agent_stopped_speaking")
    def on_agent_stop_speaking():
        """Log when agent stops speaking"""
        print("💤 Nami finished speaking")
        logger.info("Agent stopped speaking")
    
    async def start_session():
        """Start the agent session"""
        nonlocal is_awake
        
        if not is_awake:
            return
            
        print("\n" + "="*50)
        print("🤖 NAMI HOSPITAL ASSISTANT ACTIVATED")
        print("="*50)
        
        # Start the session with noise cancellation
        await session.start(
            room=ctx.room,
            agent=nami_agent,
            room_input_options=RoomInputOptions(
                audio_enabled=True,
                video_enabled=False,
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        
        logger.info("✅ Nami is awake and listening...")
        
        # Generate initial greeting
        await session.generate_reply(
            instructions=f"Greet the user as Nami, the hospital assistant robot at {HOSPITAL_NAME}. Let them know you just woke up and are ready to help with appointments, medicine delivery, navigation, and other hospital tasks.",
        )
    
    # Initial state - waiting for wake word
    print("\n" + "="*50)
    print("💤 NAMI IS SLEEPING - Say 'Hey Nami' to wake me up")
    print("Wake words:", ", ".join(WAKE_WORDS))
    print("Stop words:", ", ".join(STOP_WORDS))
    print("="*50)
    
    # Start session in sleep mode (listening for wake words but not responding)
    await session.start(
        room=ctx.room,
        agent=nami_agent,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            video_enabled=False,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Keep the agent running
    try:
        await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Agent session error: {e}")
        await session.close()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))